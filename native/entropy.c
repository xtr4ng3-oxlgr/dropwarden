/*
 * DROPWARDEN native entropy helper
 * xtr4ng3: entropy is only a signal, never a verdict.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: entropy.exe <file>\\n");
        return 1;
    }

    FILE* f = fopen(argv[1], "rb");
    if (!f) {
        fprintf(stderr, "could not open file\\n");
        return 1;
    }

    unsigned long long counts[256] = {0};
    unsigned long long total = 0;
    unsigned char buf[8192];

    while (!feof(f) && total < 2097152ULL) {
        size_t n = fread(buf, 1, sizeof(buf), f);
        for (size_t i = 0; i < n; i++) counts[buf[i]]++;
        total += n;
    }

    fclose(f);

    if (total == 0) {
        printf("0.000000\\n");
        return 0;
    }

    double entropy = 0.0;
    for (int i = 0; i < 256; i++) {
        if (counts[i] > 0) {
            double p = (double)counts[i] / (double)total;
            entropy -= p * (log(p) / log(2.0));
        }
    }

    printf("%.6f\\n", entropy);
    return 0;
}
