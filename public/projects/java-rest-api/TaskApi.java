import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * TaskAPI - a dependency-free REST API built on the JDK's built-in HTTP server.
 *
 * Demonstrates the core of backend engineering: routing, CRUD semantics, correct
 * HTTP status codes, JSON parsing/serialization, thread-pooled request handling,
 * CORS, request logging, validation, and file-backed persistence.
 *
 * Run:  java TaskApi.java [port]
 * Test: curl http://localhost:8080/api/tasks
 */
public class TaskApi {

    static final Path DATA_FILE = Path.of("tasks.json");
    static final String[] PRIORITIES = {"low", "medium", "high"};

    record Task(int id, String title, String description, String priority, boolean done, String createdAt) {
        Task with(int id, String title, String description, String priority, boolean done) {
            return new Task(id, title, description, priority, done, createdAt);
        }
    }

    static final class Store {
        private final Map<Integer, Task> tasks = new ConcurrentHashMap<>();
        private final AtomicInteger sequence = new AtomicInteger();

        Store() {
            load();
            if (tasks.isEmpty()) seed();
        }

        private void seed() {
            create("Set up CI pipeline", "Automate build and tests on push", "high");
            create("Write API documentation", "Document all endpoints with examples", "medium");
            create("Add rate limiting", "Protect public endpoints from abuse", "low");
            Task done = create("Design database schema", "Model users, tasks, and audit log", "high");
            update(done.id(), done.title(), done.description(), done.priority(), true);
        }

        synchronized Task create(String title, String description, String priority) {
            int id = sequence.incrementAndGet();
            Task task = new Task(id, title, description, priority, false, Instant.now().toString());
            tasks.put(id, task);
            save();
            return task;
        }

        synchronized Task update(int id, String title, String description, String priority, Boolean done) {
            Task current = tasks.get(id);
            if (current == null) return null;
            Task updated = current.with(
                    id,
                    title != null ? title : current.title(),
                    description != null ? description : current.description(),
                    priority != null ? priority : current.priority(),
                    done != null ? done : current.done());
            tasks.put(id, updated);
            save();
            return updated;
        }

        synchronized Task patch(int id, Task replacement) {
            if (!tasks.containsKey(id)) return null;
            Task stored = replacement.with(id, replacement.title(), replacement.description(),
                    replacement.priority(), replacement.done());
            tasks.put(id, stored);
            save();
            return stored;
        }

        synchronized boolean delete(int id) {
            boolean removed = tasks.remove(id) != null;
            if (removed) save();
            return removed;
        }

        Task get(int id) { return tasks.get(id); }

        List<Task> list(String priority, Boolean done, String query) {
            List<Task> result = new ArrayList<>();
            for (Task task : tasks.values()) {
                if (priority != null && !task.priority().equalsIgnoreCase(priority)) continue;
                if (done != null && task.done() != done) continue;
                if (query != null) {
                    String needle = query.toLowerCase();
                    boolean hit = task.title().toLowerCase().contains(needle)
                            || task.description().toLowerCase().contains(needle);
                    if (!hit) continue;
                }
                result.add(task);
            }
            result.sort((a, b) -> Integer.compare(a.id(), b.id()));
            return result;
        }

        Map<String, Object> stats() {
            Map<String, Object> byPriority = new LinkedHashMap<>();
            for (String p : PRIORITIES) byPriority.put(p, 0);
            int done = 0;
            for (Task task : tasks.values()) {
                if (task.done()) done++;
                byPriority.merge(task.priority(), 1, (a, b) -> (int) a + (int) b);
            }
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("total", tasks.size());
            result.put("done", done);
            result.put("pending", tasks.size() - done);
            result.put("byPriority", byPriority);
            return result;
        }

        synchronized void save() {
            try {
                List<Object> array = new ArrayList<>();
                for (Task task : list(null, null, null)) array.add(toMap(task));
                Files.writeString(DATA_FILE, Json.write(array));
            } catch (IOException e) {
                System.err.println("[warn] could not persist tasks: " + e.getMessage());
            }
        }

        @SuppressWarnings("unchecked")
        private void load() {
            if (!Files.exists(DATA_FILE)) return;
            try {
                Object parsed = Json.parse(Files.readString(DATA_FILE));
                if (!(parsed instanceof List<?> list)) return;
                for (Object item : list) {
                    if (!(item instanceof Map<?, ?> m)) continue;
                    Map<String, Object> map = (Map<String, Object>) m;
                    int id = (int) Json.num(map.get("id"));
                    Task task = new Task(
                            id,
                            Json.str(map.get("title")),
                            Json.str(map.get("description")),
                            Json.str(map.get("priority")),
                            Boolean.TRUE.equals(map.get("done")),
                            Json.str(map.get("createdAt")));
                    tasks.put(id, task);
                    sequence.updateAndGet(max -> Math.max(max, id));
                }
                System.out.println("[info] loaded " + tasks.size() + " task(s) from " + DATA_FILE);
            } catch (Exception e) {
                System.err.println("[warn] could not load " + DATA_FILE + ": " + e.getMessage());
            }
        }

        private static Map<String, Object> toMap(Task task) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("id", task.id());
            map.put("title", task.title());
            map.put("description", task.description());
            map.put("priority", task.priority());
            map.put("done", task.done());
            map.put("createdAt", task.createdAt());
            return map;
        }
    }

    // ------------------------------------------------------------------ JSON
    static final class Json {
        static String write(Object value) {
            StringBuilder sb = new StringBuilder();
            writeValue(sb, value);
            return sb.toString();
        }

        private static void writeValue(StringBuilder sb, Object value) {
            if (value == null) { sb.append("null"); return; }
            if (value instanceof String s) { writeString(sb, s); return; }
            if (value instanceof Boolean || value instanceof Number) { sb.append(value); return; }
            if (value instanceof Map<?, ?> map) {
                sb.append('{');
                boolean first = true;
                for (Map.Entry<?, ?> e : map.entrySet()) {
                    if (!first) sb.append(',');
                    first = false;
                    writeString(sb, String.valueOf(e.getKey()));
                    sb.append(':');
                    writeValue(sb, e.getValue());
                }
                sb.append('}');
                return;
            }
            if (value instanceof Iterable<?> it) {
                sb.append('[');
                boolean first = true;
                for (Object item : it) {
                    if (!first) sb.append(',');
                    first = false;
                    writeValue(sb, item);
                }
                sb.append(']');
                return;
            }
            writeString(sb, String.valueOf(value));
        }

        private static void writeString(StringBuilder sb, String s) {
            sb.append('"');
            for (char ch : s.toCharArray()) {
                switch (ch) {
                    case '"' -> sb.append("\\\"");
                    case '\\' -> sb.append("\\\\");
                    case '\n' -> sb.append("\\n");
                    case '\r' -> sb.append("\\r");
                    case '\t' -> sb.append("\\t");
                    default -> {
                        if (ch < 0x20) sb.append(String.format("\\u%04x", (int) ch));
                        else sb.append(ch);
                    }
                }
            }
            sb.append('"');
        }

        static Object parse(String text) {
            Parser parser = new Parser(text);
            Object value = parser.readValue();
            parser.skipWhitespace();
            if (!parser.atEnd()) throw new IllegalArgumentException("Trailing content in JSON");
            return value;
        }

        static String str(Object value) { return value == null ? null : String.valueOf(value); }

        static int num(Object value) {
            if (value instanceof Number n) return n.intValue();
            throw new IllegalArgumentException("Expected number, got " + value);
        }

        private static final class Parser {
            private final String text;
            private int index;

            Parser(String text) { this.text = text; }

            boolean atEnd() { return index >= text.length(); }

            void skipWhitespace() {
                while (index < text.length() && Character.isWhitespace(text.charAt(index))) index++;
            }

            Object readValue() {
                skipWhitespace();
                if (atEnd()) throw new IllegalArgumentException("Unexpected end of JSON");
                char ch = text.charAt(index);
                return switch (ch) {
                    case '{' -> readObject();
                    case '[' -> readArray();
                    case '"' -> readString();
                    case 't' -> readLiteral("true", Boolean.TRUE);
                    case 'f' -> readLiteral("false", Boolean.FALSE);
                    case 'n' -> readLiteral("null", null);
                    default -> readNumber();
                };
            }

            private Map<String, Object> readObject() {
                Map<String, Object> map = new LinkedHashMap<>();
                index++;
                skipWhitespace();
                if (peek() == '}') { index++; return map; }
                while (true) {
                    skipWhitespace();
                    String key = readString();
                    skipWhitespace();
                    expect(':');
                    map.put(key, readValue());
                    skipWhitespace();
                    char ch = peek();
                    if (ch == ',') { index++; continue; }
                    if (ch == '}') { index++; break; }
                    throw new IllegalArgumentException("Expected , or } in object");
                }
                return map;
            }

            private List<Object> readArray() {
                List<Object> list = new ArrayList<>();
                index++;
                skipWhitespace();
                if (peek() == ']') { index++; return list; }
                while (true) {
                    list.add(readValue());
                    skipWhitespace();
                    char ch = peek();
                    if (ch == ',') { index++; continue; }
                    if (ch == ']') { index++; break; }
                    throw new IllegalArgumentException("Expected , or ] in array");
                }
                return list;
            }

            private String readString() {
                skipWhitespace();
                expect('"');
                StringBuilder sb = new StringBuilder();
                while (true) {
                    char ch = text.charAt(index++);
                    if (ch == '"') break;
                    if (ch == '\\') {
                        char esc = text.charAt(index++);
                        switch (esc) {
                            case '"' -> sb.append('"');
                            case '\\' -> sb.append('\\');
                            case '/' -> sb.append('/');
                            case 'n' -> sb.append('\n');
                            case 'r' -> sb.append('\r');
                            case 't' -> sb.append('\t');
                            case 'b' -> sb.append('\b');
                            case 'f' -> sb.append('\f');
                            case 'u' -> {
                                sb.append((char) Integer.parseInt(text.substring(index, index + 4), 16));
                                index += 4;
                            }
                            default -> throw new IllegalArgumentException("Bad escape \\" + esc);
                        }
                    } else {
                        sb.append(ch);
                    }
                }
                return sb.toString();
            }

            private Object readNumber() {
                int start = index;
                while (index < text.length() && "-+.eE0123456789".indexOf(text.charAt(index)) >= 0) index++;
                String token = text.substring(start, index);
                if (token.isEmpty()) throw new IllegalArgumentException("Invalid number");
                if (token.contains(".") || token.contains("e") || token.contains("E")) {
                    return Double.parseDouble(token);
                }
                return Long.parseLong(token);
            }

            private Object readLiteral(String literal, Object value) {
                if (!text.startsWith(literal, index)) throw new IllegalArgumentException("Invalid literal");
                index += literal.length();
                return value;
            }

            private char peek() {
                if (atEnd()) throw new IllegalArgumentException("Unexpected end of JSON");
                return text.charAt(index);
            }

            private void expect(char ch) {
                if (peek() != ch) throw new IllegalArgumentException("Expected '" + ch + "'");
                index++;
            }
        }
    }

    // --------------------------------------------------------------- HTTP
    static final AtomicInteger REQUEST_COUNT = new AtomicInteger();

    static class ApiHandler implements HttpHandler {
        final Store store;

        ApiHandler(Store store) { this.store = store; }

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            long start = System.nanoTime();
            int status = 500;
            try {
                status = route(exchange);
            } catch (IllegalArgumentException e) {
                status = sendJson(exchange, 400, error("Bad request: " + e.getMessage()));
            } catch (Exception e) {
                status = sendJson(exchange, 500, error("Internal error: " + e.getMessage()));
            } finally {
                long ms = (System.nanoTime() - start) / 1_000_000;
                System.out.printf("%-6s %-24s -> %d (%d ms)%n",
                        exchange.getRequestMethod(), exchange.getRequestURI().getPath(), status, ms);
                exchange.close();
            }
        }

        private int route(HttpExchange exchange) throws IOException {
            Headers headers = exchange.getResponseHeaders();
            headers.add("Access-Control-Allow-Origin", "*");
            headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS");
            headers.add("Access-Control-Allow-Headers", "Content-Type");

            if (exchange.getRequestMethod().equalsIgnoreCase("OPTIONS")) {
                exchange.sendResponseHeaders(204, -1);
                return 204;
            }

            String path = exchange.getRequestURI().getPath();
            String method = exchange.getRequestMethod().toUpperCase();
            String[] parts = java.util.Arrays.stream(path.split("/"))
                    .filter(p -> !p.isBlank()).toArray(String[]::new);
            Map<String, String> query = parseQuery(exchange.getRequestURI().getRawQuery());

            if (parts.length == 1 && parts[0].equals("health")) {
                return sendJson(exchange, 200, Json.write(Map.of(
                        "status", "ok",
                        "uptime", "running",
                        "requests", REQUEST_COUNT.get())));
            }

            if (parts.length == 1 && parts[0].equals("api") && parts.length < 2) {
                return sendJson(exchange, 200, Json.write(Map.of(
                        "name", "TaskAPI", "version", "1.0",
                        "endpoints", List.of("GET /health", "GET /api/tasks", "GET /api/tasks/{id}",
                                "POST /api/tasks", "PUT /api/tasks/{id}", "PATCH /api/tasks/{id}",
                                "DELETE /api/tasks/{id}", "GET /api/stats"))));
            }

            if (parts.length >= 2 && parts[0].equals("api") && parts[1].equals("stats")) {
                if (!method.equals("GET")) return methodNotAllowed(exchange, "GET");
                return sendJson(exchange, 200, Json.write(store.stats()));
            }

            if (parts.length >= 2 && parts[0].equals("api") && parts[1].equals("tasks")) {
                Integer id = parts.length >= 3 ? parseId(parts[2]) : null;

                if (id == null) {
                    return switch (method) {
                        case "GET" -> listTasks(exchange, query);
                        case "POST" -> createTask(exchange);
                        default -> methodNotAllowed(exchange, "GET, POST");
                    };
                }
                return switch (method) {
                    case "GET" -> getTask(exchange, id);
                    case "PUT" -> putTask(exchange, id);
                    case "PATCH" -> patchTask(exchange, id);
                    case "DELETE" -> deleteTask(exchange, id);
                    default -> methodNotAllowed(exchange, "GET, PUT, PATCH, DELETE");
                };
            }

            return sendJson(exchange, 404, error("No route for " + method + " " + path));
        }

        private int listTasks(HttpExchange exchange, Map<String, String> query) throws IOException {
            Boolean done = query.containsKey("done") ? Boolean.parseBoolean(query.get("done")) : null;
            List<Object> out = new ArrayList<>();
            for (Task task : store.list(query.get("priority"), done, query.get("q"))) {
                out.add(Store.toMap(task));
            }
            return sendJson(exchange, 200, Json.write(out));
        }

        private int getTask(HttpExchange exchange, int id) throws IOException {
            Task task = store.get(id);
            if (task == null) return sendJson(exchange, 404, error("Task " + id + " not found"));
            return sendJson(exchange, 200, Json.write(Store.toMap(task)));
        }

        private int createTask(HttpExchange exchange) throws IOException {
            Map<String, Object> body = parseBody(exchange);
            String title = requireTitle(body);
            String description = Json.str(body.getOrDefault("description", ""));
            String priority = validatePriority(Json.str(body.get("priority")));
            Task task = store.create(title, description, priority);
            return sendJson(exchange, 201, Json.write(Store.toMap(task)));
        }

        private int putTask(HttpExchange exchange, int id) throws IOException {
            if (store.get(id) == null) return sendJson(exchange, 404, error("Task " + id + " not found"));
            Map<String, Object> body = parseBody(exchange);
            String title = requireTitle(body);
            Boolean done = body.containsKey("done") ? Boolean.parseBoolean(String.valueOf(body.get("done"))) : null;
            Task task = store.update(id, title,
                    Json.str(body.getOrDefault("description", "")),
                    validatePriority(Json.str(body.get("priority"))), done);
            return sendJson(exchange, 200, Json.write(Store.toMap(task)));
        }

        private int patchTask(HttpExchange exchange, int id) throws IOException {
            Task current = store.get(id);
            if (current == null) return sendJson(exchange, 404, error("Task " + id + " not found"));
            Map<String, Object> body = parseBody(exchange);
            Task patched = new Task(id,
                    body.containsKey("title") ? requireTitle(body) : current.title(),
                    body.containsKey("description") ? Json.str(body.get("description")) : current.description(),
                    body.containsKey("priority") ? validatePriority(Json.str(body.get("priority"))) : current.priority(),
                    body.containsKey("done") ? Boolean.parseBoolean(String.valueOf(body.get("done"))) : current.done(),
                    current.createdAt());
            return sendJson(exchange, 200, Json.write(Store.toMap(store.patch(id, patched))));
        }

        private int deleteTask(HttpExchange exchange, int id) throws IOException {
            if (!store.delete(id)) return sendJson(exchange, 404, error("Task " + id + " not found"));
            return sendJson(exchange, 200, Json.write(Map.of("deleted", id)));
        }

        private Map<String, Object> parseBody(HttpExchange exchange) throws IOException {
            String raw = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            if (raw.isBlank()) throw new IllegalArgumentException("Request body is required");
            Object parsed = Json.parse(raw);
            if (!(parsed instanceof Map<?, ?> map)) throw new IllegalArgumentException("Body must be a JSON object");
            @SuppressWarnings("unchecked")
            Map<String, Object> result = (Map<String, Object>) map;
            return result;
        }

        private String requireTitle(Map<String, Object> body) {
            String title = Json.str(body.get("title"));
            if (title == null || title.isBlank()) throw new IllegalArgumentException("'title' is required");
            return title.trim();
        }

        private String validatePriority(String priority) {
            if (priority == null) return "medium";
            String value = priority.toLowerCase();
            for (String allowed : PRIORITIES) if (allowed.equals(value)) return value;
            throw new IllegalArgumentException("priority must be one of low, medium, high");
        }

        private Integer parseId(String raw) {
            try {
                return Integer.parseInt(raw);
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("Invalid task id: " + raw);
            }
        }

        private static Map<String, String> parseQuery(String rawQuery) {
            Map<String, String> map = new LinkedHashMap<>();
            if (rawQuery == null) return map;
            for (String pair : rawQuery.split("&")) {
                int eq = pair.indexOf('=');
                if (eq > 0) {
                    String key = java.net.URLDecoder.decode(pair.substring(0, eq), StandardCharsets.UTF_8);
                    String val = java.net.URLDecoder.decode(pair.substring(eq + 1), StandardCharsets.UTF_8);
                    map.put(key, val);
                }
            }
            return map;
        }

        private int methodNotAllowed(HttpExchange exchange, String allowed) throws IOException {
            exchange.getResponseHeaders().add("Allow", allowed);
            return sendJson(exchange, 405, error("Method not allowed. Allowed: " + allowed));
        }
    }

    static String error(String message) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("error", message);
        return Json.write(map);
    }

    static int sendJson(HttpExchange exchange, int status, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        if (status == 204) {
            exchange.sendResponseHeaders(status, -1);
            return status;
        }
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
        return status;
    }

    public static void main(String[] args) throws IOException {
        int port = args.length > 0 ? Integer.parseInt(args[0])
                : Integer.parseInt(System.getenv().getOrDefault("PORT", "8080"));

        Store store = new Store();
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
        server.createContext("/", new ApiHandler(store));
        server.setExecutor(Executors.newFixedThreadPool(16));
        server.start();

        System.out.println("TaskAPI v1.0 running on http://localhost:" + port);
        System.out.println("Try: curl http://localhost:" + port + "/api/tasks");
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            store.save();
            System.out.println("\n[info] tasks saved, shutting down");
        }));
    }
}
