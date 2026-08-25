public class Main {
    private static final String[] SAMPLES = {
            "A man, a plan, a canal, Panama!",
            "Never odd or even",
            "Not a palindrome",
            "Madam, I'm Adam",
            "racecar",
            "Able was I, ere I saw Elba",
            "palindrome"
    };

    private static boolean isPalindrome(String s) {
        int i = 0;
        int j = s.length() - 1;
        while (i < j) {
            char a = s.charAt(i);
            char b = s.charAt(j);
            if (!Character.isLetterOrDigit(a)) {
                i++;
                continue;
            }
            if (!Character.isLetterOrDigit(b)) {
                j--;
                continue;
            }
            if (Character.toLowerCase(a) != Character.toLowerCase(b)) {
                return false;
            }
            i++;
            j--;
        }
        return true;
    }

    public static void main(String[] args) {
        int total = 0;
        for (int r = 0; r < 200000; r++) {
            for (String s : SAMPLES) {
                if (isPalindrome(s)) {
                    total++;
                }
            }
        }
        if (total == 0) {
            System.out.print("");
        }
    }
}
