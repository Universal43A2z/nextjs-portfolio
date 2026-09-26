import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.nio.file.Path;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * BankSystemGui - desktop GUI for the thread-safe banking engine (Bank.java).
 *
 * Open accounts, deposit, withdraw, and transfer money, watch the audit ledger
 * update per account, and run the concurrent stress test that proves the bank's
 * total money is conserved under parallel load.
 *
 * Run: java BankSystemGui.java
 */
public class BankSystemGui {

    private final Bank bank = new Bank();
    private final DefaultTableModel accountModel = nonEditable("Account", "Owner", "Balance (PHP)");
    private final DefaultTableModel ledgerModel = nonEditable("Type", "Amount", "Balance After", "Note", "Time");
    private final JTable accountTable = new JTable(accountModel);
    private final JTable ledgerTable = new JTable(ledgerModel);
    private final JLabel status = new JLabel(" ");
    private final JLabel invariant = new JLabel(" ");

    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {
        }
        SwingUtilities.invokeLater(() -> new BankSystemGui().show());
    }

    private static DefaultTableModel nonEditable(String... columns) {
        return new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int column) { return false; }
        };
    }

    private void show() {
        Bank.Account khent = bank.open("Khent Vincent Amorl", Bank.toCents(1_000));
        Bank.Account maria = bank.open("Maria Santos", Bank.toCents(500));
        Bank.Account jose = bank.open("Jose Rizal", Bank.toCents(250));
        bank.deposit(khent.id(), Bank.toCents(2_000), "monthly salary");
        bank.transfer(khent.id(), maria.id(), Bank.toCents(250), "shared expenses");
        bank.withdraw(jose.id(), Bank.toCents(100), "groceries");

        JFrame frame = new JFrame("BankSystem - Banking Console");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout(10, 10));

        frame.add(buildToolbar(frame), BorderLayout.NORTH);
        frame.add(buildCenter(), BorderLayout.CENTER);
        frame.add(buildStatusBar(), BorderLayout.SOUTH);

        accountTable.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        accountTable.setRowHeight(26);
        ledgerTable.setRowHeight(24);
        accountTable.getSelectionModel().addListSelectionListener(e -> {
            if (!e.getValueIsAdjusting()) refreshLedger();
        });

        refresh();
        frame.setSize(940, 640);
        frame.setMinimumSize(new Dimension(760, 480));
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }

    private JComponent buildToolbar(JFrame frame) {
        JPanel bar = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 10));
        bar.add(button("Open Account", e -> openAccount()));
        bar.add(button("Deposit", e -> deposit()));
        bar.add(button("Withdraw", e -> withdraw()));
        bar.add(button("Transfer", e -> transfer()));
        bar.add(separator());
        bar.add(button("Run Stress Test", e -> runStressTest()));
        bar.add(button("Save Ledger (CSV)", e -> saveLedger()));
        bar.add(button("Refresh", e -> refresh()));
        return bar;
    }

    private JButton button(String text, java.awt.event.ActionListener action) {
        JButton b = new JButton(text);
        b.addActionListener(action);
        return b;
    }

    private JSeparator separator() {
        JSeparator s = new JSeparator(SwingConstants.VERTICAL);
        s.setPreferredSize(new Dimension(1, 26));
        return s;
    }

    private JComponent buildCenter() {
        JPanel accounts = titled("Accounts", new JScrollPane(accountTable));
        JPanel ledger = titled("Audit Ledger (selected account)", new JScrollPane(ledgerTable));
        JSplitPane split = new JSplitPane(JSplitPane.VERTICAL_SPLIT, accounts, ledger);
        split.setResizeWeight(0.45);
        split.setBorder(BorderFactory.createEmptyBorder(0, 10, 0, 10));
        return split;
    }

    private JPanel titled(String title, JComponent body) {
        JPanel panel = new JPanel(new BorderLayout(0, 6));
        JLabel label = new JLabel(title);
        label.setFont(label.getFont().deriveFont(Font.BOLD, 14f));
        panel.add(label, BorderLayout.NORTH);
        panel.add(body, BorderLayout.CENTER);
        return panel;
    }

    private JComponent buildStatusBar() {
        JPanel bar = new JPanel(new BorderLayout());
        bar.setBorder(BorderFactory.createEmptyBorder(6, 12, 10, 12));
        status.setFont(status.getFont().deriveFont(12.5f));
        invariant.setFont(invariant.getFont().deriveFont(Font.BOLD, 12.5f));
        bar.add(status, BorderLayout.WEST);
        bar.add(invariant, BorderLayout.EAST);
        return bar;
    }

    // ------------------------------------------------------------- actions
    private void openAccount() {
        JTextField owner = new JTextField();
        JTextField opening = new JTextField("0.00");
        Object[] fields = { "Owner name:", owner, "Opening balance (PHP):", opening };
        if (JOptionPane.showConfirmDialog(accountTable, fields, "Open Account",
                JOptionPane.OK_CANCEL_OPTION) != JOptionPane.OK_OPTION) {
            return;
        }
        if (owner.getText().isBlank()) {
            error("Owner name is required.");
            return;
        }
        Long cents = parseAmount(opening.getText(), true);
        if (cents == null) return;
        bank.open(owner.getText().trim(), cents);
        refresh();
        selectLast();
    }

    private void deposit() {
        Bank.Account account = chooseAccount("Deposit into which account?", selectedAccount());
        if (account == null) return;
        Long cents = askAmount("Deposit amount (PHP):");
        if (cents == null) return;
        try {
            bank.deposit(account.id(), cents, "GUI deposit");
            afterChange("Deposited " + Bank.money(cents) + " into " + account.id(), account);
        } catch (RuntimeException ex) {
            error(ex.getMessage());
        }
    }

    private void withdraw() {
        Bank.Account account = chooseAccount("Withdraw from which account?", selectedAccount());
        if (account == null) return;
        Long cents = askAmount("Withdraw amount (PHP):");
        if (cents == null) return;
        try {
            bank.withdraw(account.id(), cents, "GUI withdrawal");
            afterChange("Withdrew " + Bank.money(cents) + " from " + account.id(), account);
        } catch (RuntimeException ex) {
            error(ex.getMessage());
        }
    }

    private void transfer() {
        List<Bank.Account> accounts = bank.all();
        if (accounts.size() < 2) {
            error("You need at least two accounts to transfer.");
            return;
        }
        Bank.Account from = chooseAccount("Transfer from:", selectedAccount());
        if (from == null) return;
        Bank.Account to = chooseAccount("Transfer to:", accounts.get(0) == from ? accounts.get(1) : accounts.get(0));
        if (to == null) return;
        if (from.id().equals(to.id())) {
            error("Source and destination must be different accounts.");
            return;
        }
        Long cents = askAmount("Transfer amount (PHP):");
        if (cents == null) return;
        try {
            bank.transfer(from.id(), to.id(), cents, "GUI transfer");
            afterChange("Transferred " + Bank.money(cents) + " from " + from.id() + " to " + to.id(), from);
        } catch (RuntimeException ex) {
            error(ex.getMessage());
        }
    }

    private void runStressTest() {
        final int threads = 8;
        final int perThread = 500;
        final long baseline = bank.totalCents();
        invariant.setForeground(Color.DARK_GRAY);
        invariant.setText("Stress test running...");

        new SwingWorker<Long, Void>() {
            @Override
            protected Long doInBackground() throws Exception {
                List<Bank.Account> accounts = bank.all();
                ExecutorService pool = Executors.newFixedThreadPool(threads);
                for (int t = 0; t < threads; t++) {
                    final int seed = t;
                    pool.submit(() -> {
                        Random rng = new Random(seed);
                        for (int i = 0; i < perThread; i++) {
                            Bank.Account from = accounts.get(rng.nextInt(accounts.size()));
                            Bank.Account to = accounts.get(rng.nextInt(accounts.size()));
                            if (from == to) continue;
                            long amount = (rng.nextInt(50) + 1) * 100L;
                            try {
                                bank.transfer(from.id(), to.id(), amount, "stress");
                            } catch (IllegalStateException ignored) {
                                // insufficient funds under load is expected
                            }
                        }
                    });
                }
                pool.shutdown();
                pool.awaitTermination(30, TimeUnit.SECONDS);
                return bank.totalCents();
            }

            @Override
            protected void done() {
                try {
                    long closing = get();
                    boolean conserved = closing == baseline;
                    invariant.setForeground(conserved ? new Color(0, 140, 90) : Color.RED.darker());
                    invariant.setText((conserved ? "Money conserved: YES" : "MONEY CONSERVED: NO - RACE!")
                            + "   (" + bank.transfers() + " transfers)");
                    refresh();
                    JOptionPane.showMessageDialog(accountTable,
                            "Concurrent simulation finished.\n\n"
                                    + threads + " threads x " + perThread + " transfers\n"
                                    + "Baseline total: " + Bank.money(baseline) + "\n"
                                    + "Closing total:  " + Bank.money(closing) + "\n\n"
                                    + (conserved ? "Invariant held - no money lost or created."
                                                 : "Invariant violated - race condition detected!"),
                            "Stress Test", JOptionPane.INFORMATION_MESSAGE);
                } catch (Exception ex) {
                    error("Stress test failed: " + ex.getMessage());
                }
            }
        }.execute();
    }

    private void saveLedger() {
        try {
            Path file = Path.of("ledger.csv");
            bank.persist(file);
            info("Audit ledger saved to " + file.toAbsolutePath());
        } catch (Exception ex) {
            error("Could not save ledger: " + ex.getMessage());
        }
    }

    // -------------------------------------------------------------- helpers
    private void afterChange(String message, Bank.Account account) {
        refresh();
        if (account != null) select(account.id());
        invariant.setForeground(new Color(0, 120, 200));
        invariant.setText(message);
    }

    private void refresh() {
        accountModel.setRowCount(0);
        for (Bank.Account account : bank.all()) {
            accountModel.addRow(new Object[]{
                    account.id(), account.owner(), Bank.money(account.balanceCents())});
        }
        refreshLedger();
        status.setText(String.format("Accounts: %d      Total money: %s      Transfers: %d",
                bank.all().size(), Bank.money(bank.totalCents()), bank.transfers()));
    }

    private void refreshLedger() {
        ledgerModel.setRowCount(0);
        Bank.Account account = selectedAccount();
        if (account == null) return;
        List<Bank.Transaction> transactions = account.ledger();
        java.time.format.DateTimeFormatter fmt = java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss");
        for (int i = transactions.size() - 1; i >= 0; i--) {
            Bank.Transaction tx = transactions.get(i);
            ledgerModel.addRow(new Object[]{
                    tx.type().name(),
                    Bank.money(tx.amountCents()),
                    Bank.money(tx.balanceAfterCents()),
                    tx.note(),
                    tx.at().format(fmt)});
        }
    }

    private Bank.Account selectedAccount() {
        int row = accountTable.getSelectedRow();
        List<Bank.Account> accounts = bank.all();
        if (row < 0 || row >= accounts.size()) {
            return accounts.isEmpty() ? null : accounts.get(0);
        }
        return accounts.get(row);
    }

    private void select(String accountId) {
        List<Bank.Account> accounts = bank.all();
        for (int i = 0; i < accounts.size(); i++) {
            if (accounts.get(i).id().equals(accountId)) {
                accountTable.setRowSelectionInterval(i, i);
                return;
            }
        }
    }

    private void selectLast() {
        int last = accountModel.getRowCount() - 1;
        if (last >= 0) accountTable.setRowSelectionInterval(last, last);
    }

    private Bank.Account chooseAccount(String message, Bank.Account preselect) {
        List<Bank.Account> accounts = bank.all();
        if (accounts.isEmpty()) {
            error("No accounts yet. Open an account first.");
            return null;
        }
        Object choice = JOptionPane.showInputDialog(accountTable, message, "Select Account",
                JOptionPane.QUESTION_MESSAGE, null, accounts.toArray(),
                preselect != null ? preselect : accounts.get(0));
        return (Bank.Account) choice;
    }

    private Long askAmount(String prompt) {
        String input = JOptionPane.showInputDialog(accountTable, prompt, "Amount",
                JOptionPane.QUESTION_MESSAGE);
        if (input == null) return null;
        return parseAmount(input, false);
    }

    private Long parseAmount(String input, boolean allowZero) {
        try {
            double pesos = Double.parseDouble(input.replace(",", "").trim());
            long cents = Bank.toCents(pesos);
            if (cents < 0 || (!allowZero && cents == 0)) throw new NumberFormatException();
            return cents;
        } catch (NumberFormatException ex) {
            error("Invalid amount: \"" + input + "\"");
            return null;
        }
    }

    private void error(String message) {
        JOptionPane.showMessageDialog(accountTable, message, "BankSystem", JOptionPane.ERROR_MESSAGE);
    }

    private void info(String message) {
        JOptionPane.showMessageDialog(accountTable, message, "BankSystem", JOptionPane.INFORMATION_MESSAGE);
    }
}
