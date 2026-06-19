import java.util.HashMap;
import java.util.Map;

public class Main {
    private static final String[][] PAIRS = {
            {"listen", "silent"},
            {"rail safety", "fairy tales"},
            {"dormitory", "dirty room"},
            {"the eyes", "they see"},
            {"not an anagram", "definitely not"},
            {"A gentleman", "elegant man"},
            {"Clint Eastwood", "old west action"}
    };

    private static String normalize(String s) {
        StringBuilder out = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isLetterOrDigit(c)) {
                out.append(Character.toLowerCase(c));
            }
        }
        return out.toString();
    }

    private static boolean isAnagram(String a, String b) {
        String na = normalize(a);
        String nb = normalize(b);
        if (na.length() != nb.length()) {
            return false;
        }
        Map<Character, Integer> counts = new HashMap<>();
        for (int i = 0; i < na.length(); i++) {
            char ca = na.charAt(i);
            char cb = nb.charAt(i);
            counts.put(ca, counts.getOrDefault(ca, 0) + 1);
            counts.put(cb, counts.getOrDefault(cb, 0) - 1);
        }
        for (int v : counts.values()) {
            if (v != 0) {
                return false;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        int total = 0;
        for (int r = 0; r < 200000; r++) {
            for (String[] p : PAIRS) {
                if (isAnagram(p[0], p[1])) {
                    total++;
                }
            }
        }
        if (total == 0) {
            System.out.print("");
        }
    }
}
