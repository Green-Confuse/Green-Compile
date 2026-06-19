import java.util.PriorityQueue;

class Main implements Comparable<Main> {
    final int priority;
    final String name;

    public Main(int p, String n) {
        priority = p;
        name = n;
    }

    public String toString() {
        return priority + ", " + name;
    }

    public int compareTo(Main other) {
        return priority < other.priority ? -1 : priority > other.priority ? 1 : 0;
    }

    public static void main(String[] args) {
        PriorityQueue<Main> pq = new PriorityQueue<Main>();
        pq.add(new Main(3, "Clear drains"));
        pq.add(new Main(4, "Feed cat"));
        pq.add(new Main(5, "Make tea"));
        pq.add(new Main(1, "Solve RC tasks"));
        pq.add(new Main(2, "Tax return"));

        while (!pq.isEmpty())
            System.out.println(pq.remove());
    }
}