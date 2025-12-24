#ifndef DEALER_H
#define DEALER_H

#include <string>
#include <filesystem>

using namespace std;
namespace fs = std::filesystem;

class Dealer{
    fs::path dir;

public:
    bool path_exists(const fs::path& p, fs::file_status s);
    fs::path get_dir();
    bool set_dir(const fs::path p);
    Dealer();

};

#endif