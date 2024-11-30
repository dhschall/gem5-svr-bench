

#include <iostream>
#include <cstdlib>
#include <algorithm>

#include "m5ops.h"


class BranchArray
{
    int array_size;
    const int LOOP = 10;
    bool m5_on = false;
    
uint64_t *A;

public:
    BranchArray()
    : array_size(0),
        A(nullptr)
     {}
    ~BranchArray() {
        delete[] A;
    }


    bool init(int _array_size, bool sorted = false, bool m5ops_enabled = false)
    {
        array_size = _array_size;
        m5_on = m5ops_enabled;

        A = new uint64_t[array_size];
        for (int i = 0; i < array_size; i++)
        {
            A[i] = std::rand() % 256;
        }

        if (sorted)
        {
            std::sort(A, A + array_size);
        }

        return true;
    }



int exec()
{
	// Call the assembly
	// res_val =  singlestride(A, stride, num_iterations);
    int res_val = 0;

	for (unsigned i = 0; i < LOOP; ++i)
	{
        if (m5_on)
            m5_reset_stats(0, 0);

		for (unsigned c = 0; c < array_size; ++c)
		{
		if (A[c] >= 128)
			res_val += A[c];

		if (A[c] >= 32)
			res_val += A[c];

		if (A[c] >= 4)
			res_val -= A[c];

		if (A[c] >= 3)
			res_val *= A[c];

		if (A[c] < 53)
			res_val |= A[c];

		if (A[c] < 9)
			res_val |= A[c];

		if (A[c] < 2)
			res_val &= A[c];

		if (A[c] < 1)
			res_val ^= A[c];

		if (A[c] > 0)
			res_val += A[c];

		}

        if (m5_on)
            m5_dump_stats(0, 0);

        printf("Iter:%d = Sum: %d\n", i, res_val);
	}
    return res_val;
}

};


int main(int argc, char **argv)
{
    if (argc < 2)
    {
        std::cerr << "Usage: " << argv[0] << " <array_size> [m5opt]" << std::endl;
        return 1;
    }

    const int ARRAY_SIZE = std::stoi(argv[1]);
    bool M5OPS_ENABLED = false;
    if (argc > 2)
    {
        M5OPS_ENABLED = true;
    }
    BranchArray b;

    b.init(ARRAY_SIZE, false, M5OPS_ENABLED);

    auto r = b.exec();

    std::cout << r << std::endl;
    return 0;
}