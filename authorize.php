<?php
  //$fields = array(
    //'authorized' => 'true',
    //'postToken' => '6' //'$_POST['preToken']'
  //);
  //http_post_fields("https://kjd.mtv.corp.google.com:8888/issuexsrf", $fields);
?>

<?php
$fields = array(
    'name' => 'mike',
        'pass' => 'se_ret'
        );
$files = array(
    array(
            'name' => 'uimg',
                    'type' => 'image/jpeg',
                            'file' => 'authorize.php',
                                )
    );

$response = http_post_fields("http://www.example.com/", $fields, $files);
?>
