import java.nio.file.Path;
import java.util.Random;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * BankSystem - command-line demo of the thread-safe banking engine (see Bank.java).
 *
 * Runs a concurrent transfer simulation and verifies the total-balance invariant,
 * then writes a full audit ledger to ledger.csv.
 *
 * Run: java BankSystem.java
 */
public class BankSystem {

    public static void main(String[] args) throws Exception {
        Bank bank = new Bank();
        Bank.Account alice = bank.open("Khent Vincent Amorl", Bank.toCents(1_000));
        Bank.Account bob = bank.open("Maria Santos", Bank.toCents(500));
        Bank.Account carl = bank.open("Jose Rizal", Bank.toCents(250));

        System.out.println("=== BankSystem (CLI) ===");
        long openingTotal = bank.totalCents();
        System.out.printf("Opening total: %s across %d accounts%n%n", Bank.money(openingTotal), bank.all().size());

        bank.deposit(alice.id(), Bank.toCents(2_000), "salary");
        bank.withdraw(bob.id(), Bank.toCents(100), "grocery");

        long baselineTotal = bank.totalCents();
        System.out.printf("After seed activity: %s%n%n", Bank.money(baselineTotal));

        int threads = 8;
        int transfersPerThread = 500;
        ExecutorService pool = Executors.newFixedThreadPool(threads);
        Bank.Account[] ring = { alice, bob, carl };

        for (int t = 0; t < threads; t++) {
            final int seed = t;
            pool.submit(() -> {
                Random rng = new Random(seed);
                for (int i = 0; i < transfersPerThread; i++) {
                    Bank.Account from = ring[rng.nextInt(ring.length)];
                    Bank.Account to = ring[rng.nextInt(ring.length)];
                    if (from == to) continue;
                    long amount = (rng.nextInt(50) + 1) * 100L;
                    try {
                        bank.transfer(from.id(), to.id(), amount, "concurrent");
                    } catch (IllegalStateException ignored) {
                        // insufficient funds under load is an expected branch
                    }
                }
            });
        }

        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);

        System.out.println("Concurrent simulation (8 threads x 500 transfers):");
        for (Bank.Account account : bank.all()) {
            System.out.printf("  %-9s %-22s %s%n", account.id(), account.owner(), Bank.money(account.balanceCents()));
        }

        long closingTotal = bank.totalCents();
        System.out.printf("%nTransfers executed : %d%n", bank.transfers());
        System.out.printf("Opening total      : %s%n", Bank.money(openingTotal));
        System.out.printf("Baseline total     : %s%n", Bank.money(baselineTotal));
        System.out.printf("Closing total      : %s%n", Bank.money(closingTotal));
        System.out.printf("Money conserved    : %s%n", baselineTotal == closingTotal ? "YES" : "NO - RACE DETECTED");

        bank.persist(Path.of("ledger.csv"));
        System.out.printf("Audit ledger wrote : %s%n", Path.of("ledger.csv").toAbsolutePath());

        if (baselineTotal != closingTotal) System.exit(1);
    }
}
