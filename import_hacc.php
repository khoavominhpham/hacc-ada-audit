<?php
use Drupal\node\Entity\Node;

// 1. Locate the JSON file using the absolute directory path
$json_file = __DIR__ . '/ml_pipeline/data/hacc_scraped.json';

if (!file_exists($json_file)) {
    die("Error: Could not find the scraped JSON file. Run the Python script first!\n");
}

$data = json_decode(file_get_contents($json_file), TRUE);

// 2. Loop through the scraped pages and create a Drupal node for each
foreach ($data as $item) {
    $node = Node::create([
        'type'        => 'basic_page', 
        'title'       => substr($item['title'], 0, 255),
        'field_body'  => [ 
            'value'   => $item['body'],
            'format'  => 'full_html', 
        ],
    ]);
    
    $node->setPublished(TRUE);
    $node->save();
    
    echo "✅ Automatically created Drupal node: " . $item['title'] . "\n";
}

echo "\n🎉 Successfully imported all HACC pages!\n";