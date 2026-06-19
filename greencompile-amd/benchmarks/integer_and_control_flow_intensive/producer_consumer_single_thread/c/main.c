#include <stdio.h>

#define CAPACITY 256
#define ITEMS_PER_ROUND 5000
#define ROUNDS 200

int main(void) {
    int buffer[CAPACITY];
    int head = 0;
    int tail = 0;
    int count = 0;
    long checksum = 0;

    for (int r = 0; r < ROUNDS; r++) {
        int produced = 0;
        int consumed = 0;
        while (consumed < ITEMS_PER_ROUND) {
            if (produced < ITEMS_PER_ROUND && count < CAPACITY) {
                buffer[tail] = produced + r;
                tail = (tail + 1) % CAPACITY;
                count++;
                produced++;
            }
            if (count > 0) {
                int value = buffer[head];
                head = (head + 1) % CAPACITY;
                count--;
                checksum += value;
                consumed++;
            }
        }
    }

    volatile long sink = checksum;
    (void)sink;
    return 0;
}
