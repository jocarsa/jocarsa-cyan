<?php

/**
 * Simple class to interface with the C++ "database" engine (mydbapp).
 */
class SimpleFileDB
{
    private $executable;
    private $databaseName;

    /**
     * Constructor
     *
     * @param string $executable   Path to the compiled C++ program (e.g. ./mydbapp).
     * @param string $databaseName Name of the "database" folder (e.g. MyDatabase).
     */
    public function __construct($databaseName)
    {
        $this->executable   = "/usr/local/bin/cyan.out";
        $this->databaseName = $databaseName;
    }

    /**
     * Select operation:
     * Calls the C++ program with "select" to list all .json files in the database folder.
     * Returns the raw output or parsed data.
     */
    public function select($parseJson = false)
    {
        // Build the shell command safely:
        $cmd = escapeshellcmd($this->executable) . ' ' 
             . escapeshellarg($this->databaseName) . ' select';

        // Execute:
        $output = shell_exec($cmd);
        if ($output === null) {
            throw new RuntimeException("Failed to execute select command.");
        }

        // Option 1: Return raw output as a string
        if (!$parseJson) {
            return $output;
        }

        // Option 2: Parse the output into an array structure
        //    - The C++ program prints something like:
        //        File: record_123456789.json
        //        Content:
        //        { ... json data ... }
        //      (followed by a blank line before the next record)
        //
        // We can parse these lines. This is a simple approach and
        // relies on the specific output format of the C++ program.

        $lines = explode("\n", $output);
        $results = [];
        $currentFile = null;
        $currentJson = "";

        for ($i = 0; $i < count($lines); $i++) {
            $line = trim($lines[$i]);
            if (strpos($line, 'File: ') === 0) {
                // Found the start of a new record
                // If there's an existing record pending, store it first
                if ($currentFile !== null && strlen($currentJson) > 0) {
                    // Attempt to decode JSON
                    $decoded = json_decode($currentJson, true);
                    // Fallback: store raw if decoding fails
                    $results[] = [
                        'file' => $currentFile,
                        'data' => $decoded ?? $currentJson
                    ];
                }
                // Reset
                $currentFile = substr($line, strlen('File: '));
                $currentJson = "";
            } elseif ($line === 'Content:' || $line === '') {
                // We skip these literal lines
                continue;
            } else {
                // This should be part of the JSON
                // If there's multiple lines, append
                $currentJson .= ($currentJson === "" ? $line : "\n".$line);
            }
        }

        // After loop ends, flush the last record if any
        if ($currentFile !== null && strlen($currentJson) > 0) {
            $decoded = json_decode($currentJson, true);
            $results[] = [
                'file' => $currentFile,
                'data' => $decoded ?? $currentJson
            ];
        }

        return $results;
    }

    /**
     * Insert operation:
     * Calls the C++ program with "insert" to insert JSON data into the database.
     *
     * @param string|array $jsonData The data to insert (raw JSON string or PHP array).
     * @return string Output from the C++ program.
     */
    public function insert($jsonData)
    {
        // If the user passes an array, convert to JSON
        if (is_array($jsonData)) {
            $jsonData = json_encode($jsonData, JSON_UNESCAPED_SLASHES);
        }

        // Build the shell command safely:
        //   - escapeshellarg for the JSON data to handle special chars
        $cmd = escapeshellcmd($this->executable) . ' '
             . escapeshellarg($this->databaseName) . ' insert '
             . escapeshellarg($jsonData);

        $output = shell_exec($cmd);
        if ($output === null) {
            throw new RuntimeException("Failed to execute insert command.");
        }

        return $output;
    }
}


