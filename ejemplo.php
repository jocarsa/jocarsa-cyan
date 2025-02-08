<?php
require 'conectorphp.php';

// Instantiate our class
$db = new SimpleFileDB('clientes');

// Insert some data
$dataToInsert = ['nombre' => 'Francisco', 'age' => 25];
$insertResult = $db->insert($dataToInsert);
echo "Insert result: " . $insertResult . "\n";

// Select the data and parse it
$rows = $db->select($parseJson = true);

echo "Select result (parsed):\n";
print_r($rows);

