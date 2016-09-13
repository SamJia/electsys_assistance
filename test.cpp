#include <vector>
#include <cstdio>
using namespace std;

template <typename T, int size>
class array
{
public:
	array(){}
	~array(){}
	T &operator[](int pos) {
		if (pos < 0 || pos > size) {
			printf("wrong\n");
			double b = 1/0.0;
			printf("%f\n", b);
		}
		return a[pos];
	}
	T a[size];
};

int main() {
	array<int, 10> a;
	a[0] = 100;
	printf("%d\n", a[0]);
	printf("%d\n", a[11]);
}