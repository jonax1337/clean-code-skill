import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Stream;
import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;

/**
 * Builds and tests the project without Maven or Gradle: {@code java tools/RunTests.java}.
 *
 * <p>Compiles every source under {@code src/} into {@code build/classes} and runs all JUnit 5 tests found there
 * with the console launcher in {@code lib/}. With a directory argument, for example {@code .hidden}, it also
 * compiles that directory against the project and runs only the tests in it.
 */
public class RunTests {
    private static final Path JUNIT = Path.of("lib", "junit-platform-console-standalone.jar");
    private static final Path PROJECT_CLASSES = Path.of("build", "classes");
    private static final Path EXTRA_CLASSES = Path.of("build", "extra-classes");

    public static void main(String[] args) throws IOException, InterruptedException {
        compileOrExit(Path.of("src"), PROJECT_CLASSES, JUNIT.toString());
        Path testClasses = PROJECT_CLASSES;
        if (args.length > 0) {
            compileOrExit(Path.of(args[0]), EXTRA_CLASSES, classPath(PROJECT_CLASSES, JUNIT));
            testClasses = EXTRA_CLASSES;
        }
        System.exit(runJUnit(testClasses));
    }

    private static void compileOrExit(Path sources, Path output, String classPath) throws IOException {
        deleteRecursively(output);
        Files.createDirectories(output);
        List<String> arguments = new ArrayList<>(List.of("-d", output.toString(), "-cp", classPath, "-Xlint:all"));
        arguments.addAll(javaFiles(sources));
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        int status = compiler.run(null, null, null, arguments.toArray(String[]::new));
        if (status != 0) {
            System.err.println("Compilation of " + sources + " failed.");
            System.exit(status);
        }
    }

    private static int runJUnit(Path testClasses) throws IOException, InterruptedException {
        String java = ProcessHandle.current().info().command().orElse("java");
        Process launcher = new ProcessBuilder(
                        java, "-jar", JUNIT.toString(), "execute",
                        "--class-path", classPath(testClasses, PROJECT_CLASSES),
                        "--scan-class-path", testClasses.toString(),
                        "--disable-banner", "--disable-ansi-colors", "--details=tree")
                .inheritIO()
                .start();
        return launcher.waitFor();
    }

    private static String classPath(Path... entries) {
        return String.join(File.pathSeparator, Stream.of(entries).map(Path::toString).toList());
    }

    private static List<String> javaFiles(Path root) throws IOException {
        try (Stream<Path> paths = Files.walk(root)) {
            return paths.filter(path -> path.toString().endsWith(".java")).map(Path::toString).sorted().toList();
        }
    }

    private static void deleteRecursively(Path root) throws IOException {
        if (!Files.exists(root)) {
            return;
        }
        try (Stream<Path> paths = Files.walk(root)) {
            for (Path path : paths.sorted(Comparator.reverseOrder()).toList()) {
                Files.delete(path);
            }
        }
    }
}
