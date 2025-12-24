#include "dealer.h"

//yoinked here https://en.cppreference.com/w/cpp/filesystem/exists.html
bool Dealer::path_exists(const fs::path& p, fs::file_status s = fs::file_status{}){
    if (fs::status_known(s) ? fs::exists(s) : fs::exists(p)) return true;
    else return false;
}

fs::path Dealer::get_dir(){
    return dir;
}

bool Dealer::set_dir(fs::path p){
    if(path_exists(p)){
        dir = p;
        return true;
    }
    return false;
}

Dealer::Dealer(){
    fs::path p = fs::current_path();
    set_dir(p);
}