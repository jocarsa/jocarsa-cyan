#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <chrono>
#include <ctime>

int main(int argc, char* argv[])
{
    // Simple usage check
    // Expected usage:
    //   1) <program> <databaseName> select
    //   2) <program> <databaseName> insert <jsonData>
    //
    // Example:
    //   mydbapp MyDatabase select
    //   mydbapp MyDatabase insert "{\"name\":\"John\",\"age\":30}"

    if (argc < 3) {
        std::cerr << "Usage:\n"
                  << "  " << argv[0] << " <databaseName> select\n"
                  << "  " << argv[0] << " <databaseName> insert <jsonData>\n";
        return 1;
    }

    // Extract arguments
    std::string databaseName = argv[1];
    std::string operation    = argv[2];

    // Ensure the database folder exists
    // If it doesn't exist, create it.
    try {
        std::filesystem::create_directories(databaseName);
    } catch (const std::exception &ex) {
        std::cerr << "Error creating/checking directory: " << ex.what() << '\n';
        return 1;
    }

    if (operation == "select") {
        // No extra parameter needed
        // List all files in the database folder and print their contents
        try {
            for (const auto& entry : std::filesystem::directory_iterator(databaseName)) {
                if (entry.is_regular_file() && entry.path().extension() == ".json") {
                    // Read file
                    std::ifstream ifs(entry.path());
                    if (!ifs) {
                        std::cerr << "Error opening file: " << entry.path() << '\n';
                        continue;
                    }

                    std::string content((std::istreambuf_iterator<char>(ifs)),
                                         std::istreambuf_iterator<char>());

                    // Print file name and contents
                    std::cout << "File: " << entry.path().filename().string() << '\n';
                    std::cout << "Content:\n" << content << "\n\n";
                }
            }
        } catch (const std::exception &ex) {
            std::cerr << "Error reading directory contents: " << ex.what() << '\n';
            return 1;
        }
    }
    else if (operation == "insert") {
        // We need one more parameter for JSON data
        if (argc < 4) {
            std::cerr << "Error: Missing JSON data for insert operation.\n";
            return 1;
        }

        // The JSON (raw) data to be inserted
        std::string jsonData = argv[3];

        // Create a filename based on current time (or any other strategy).
        // For uniqueness, we'll use "record_<unixTimestamp>.json"
        auto now = std::chrono::system_clock::now();
        auto now_c = std::chrono::system_clock::to_time_t(now);

        std::string fileName = "record_" + std::to_string(now_c) + ".json";
        std::filesystem::path filePath = std::filesystem::path(databaseName) / fileName;

        // Write the file
        try {
            std::ofstream ofs(filePath);
            if (!ofs) {
                std::cerr << "Error creating file: " << filePath.string() << '\n';
                return 1;
            }
            ofs << jsonData;
            ofs.close();
            std::cout << "Data inserted successfully into: " << filePath.string() << '\n';
        } catch (const std::exception &ex) {
            std::cerr << "Error writing file: " << ex.what() << '\n';
            return 1;
        }
    }
    else {
        std::cerr << "Error: Unknown operation '" << operation << "'. Use 'select' or 'insert'.\n";
        return 1;
    }

    return 0;
}

