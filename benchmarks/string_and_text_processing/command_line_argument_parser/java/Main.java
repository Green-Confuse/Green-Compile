public class Main {
    public static void main(String[] args) {
        String mode = "default";
        String name = "unknown";
        int size = 0;
        int repeat = 0;
        int verbose = 0;

        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--mode":
                    if (i + 1 < args.length) {
                        mode = args[++i];
                    }
                    break;
                case "--name":
                    if (i + 1 < args.length) {
                        name = args[++i];
                    }
                    break;
                case "--size":
                    if (i + 1 < args.length) {
                        size = parseInt(args[++i]);
                    }
                    break;
                case "--repeat":
                    if (i + 1 < args.length) {
                        repeat = parseInt(args[++i]);
                    }
                    break;
                case "--verbose":
                    verbose = 1;
                    break;
                default:
                    break;
            }
        }

        if (mode.length() + name.length() + size + repeat + verbose == 0) {
            System.out.print("");
        }
    }

    private static int parseInt(String s) {
        int value = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c >= '0' && c <= '9') {
                value = value * 10 + (c - '0');
            }
        }
        return value;
    }
}
