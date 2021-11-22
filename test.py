from add_package_old import *

def test_sum():
    standard_dict = set_dict_with_standard_values("hello")
    assert standard_dict == 5, "Should be 5"

if __name__ == "__main__":
    test_sum()
    print("Everything passed")