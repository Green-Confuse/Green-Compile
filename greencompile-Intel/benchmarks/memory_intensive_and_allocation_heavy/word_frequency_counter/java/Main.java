import java.util.HashMap;
import java.util.Map;

public class Main {
    private static final String TEXT =
            "GreenCompile evaluates energy efficiency across CPU architectures. " +
            "The word frequency counter parses text and counts repeated words. " +
            "This benchmark stresses string handling, hashing, and memory access patterns.";

    private static void countWords(Map<String, Integer> freq, String text) {
        StringBuilder buf = new StringBuilder();
        for (int i = 0; i <= text.length(); i++) {
            char c = (i < text.length()) ? text.charAt(i) : '\0';
            if (Character.isLetterOrDigit(c)) {
                buf.append(Character.toLowerCase(c));
            } else if (buf.length() > 0) {
                String word = buf.toString();
                freq.put(word, freq.getOrDefault(word, 0) + 1);
                buf.setLength(0);
            }
        }
    }

    public static void main(String[] args) {
        Map<String, Integer> freq = new HashMap<>();
        for (int i = 0; i < 500; i++) {
            countWords(freq, TEXT);
        }

        long checksum = 0;
        for (Map.Entry<String, Integer> e : freq.entrySet()) {
            checksum += (long) e.getValue() * e.getKey().length();
        }
        if (checksum == 0) {
            System.out.print("");
        }
    }
}
