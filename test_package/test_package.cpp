#include <LexActivator.h>
#include <stdlib.h>

int main() {
#if _WIN32
	int status = SetProductData(L"foo");
#else
	int status = SetProductData("bar");
#endif
	if (LA_OK == status)
	{
		return EXIT_FAILURE;
	}
    return EXIT_SUCCESS;
}

