

#include <iostream>
#include <cstdlib>
#include <algorithm>

#include <bits/stdc++.h>

#include "m5ops.h"


class BinarySearch

{
    int array_size;
    const int LOOP = 3;
    bool m5_on = false;
    
    std::vector<int> A;

public:
    BinarySearch()
    : array_size(0)
     {}


    bool init(int _array_size, bool m5ops_enabled = false)
    {
        array_size = _array_size;
        m5_on = m5ops_enabled;

        A.resize(array_size);
        for (int i = 0; i < array_size; i++)
        {
            A[i] = std::rand() % 256;
            // printf("A[%d] = %d\n", i, A[i]);
        }
        return true;
    }

int Binary_search(std::vector<int>x,int target){
    int maximum=(x.size())-1;
    int minimum = 0;
    int mean;
    while (maximum>minimum){
        mean = (maximum+minimum)/2;
        if (x[mean] == target){
            // std::cout << "The number you're looking for is found! \n";
            return mean;
        }
        else if(x[mean] > target){
            maximum = (mean-1);
        }
        else{
            minimum = (mean+1);
        }
    }
    return -1;
}


int exec()
{
	// Call the assembly
	// res_val =  singlestride(A, stride, num_iterations);
    int res_val = 0;
    const auto keys = {1, 103, 3, 4, 81, 6, 7, 26, 9, 10};

	for (unsigned i = 0; i < LOOP; ++i)
	{
        if (m5_on)
            m5_reset_stats(0, 0);
        
        res_val = 0;

        // for (int i = 0; i < array_size; i++)
        // {
        //     printf("A[%d] = %d\n", i, A[i]);
        // }


        for (const auto key : keys)
        {
            // auto f = std::binary_search(A.begin(), A.end(), key);
            auto f = Binary_search(A, key);
            res_val += f;
            // printf("Searching for key: %d -> %d, %s\n", key, f, (f > 0) ? "Found" : "Not Found");
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
    BinarySearch b;

    b.init(ARRAY_SIZE, M5OPS_ENABLED);

    auto r = b.exec();

    std::cout << r << std::endl;
    return 0;
}