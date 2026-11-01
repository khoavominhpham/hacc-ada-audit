<?php

use Drupal\node\Entity\Node;

// 1. Locate the JSON file using the absolute directory path
$json_file = __DIR__ . '/ml_pipeline/data/hacc_scraped.json';

if (!file_exists($json_file)) {
    die("Error: Could not find the scraped JSON file. Run the Python script first!\n");
}

$data = json_decode(file_get_contents($json_file), TRUE);
$created = 0;
$updated = 0;

// 2. Loop through the scraped pages: update if title exists, otherwise create
foreach ($data as $item) {
    $title = substr($item['title'], 0, 255);

    $existing_nids = \Drupal::entityQuery('node')
        ->condition('type', 'basic_page')
        ->condition('title', $title)
        ->accessCheck(FALSE)
        ->execute();

    if (!empty($existing_nids)) {
        $nid = reset($existing_nids);
        $node = Node::load($nid);
        $node->set('field_body', [
            'value'  => $item['body'],
            'format' => 'full_html',
        ]);
        $node->save();
        $updated++;
        echo "🔄 Updated existing Drupal node: " . $title . "\n";
    } else {
        $node = Node::create([
            'type'       => 'basic_page',
            'title'      => $title,
            'field_body' => [
                'value'  => $item['body'],
                'format' => 'full_html',
            ],
        ]);
        $node->setPublished(TRUE);
        $node->save();
        $created++;
        echo "✅ Created new Drupal node: " . $title . "\n";
    }
}

echo "\n🎉 Sync complete! Updated $updated pages and created $created new HACC pages!\n";