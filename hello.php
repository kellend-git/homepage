<?php
  echo 'Booking a listing with ID: ' . htmlspecialchars($_GET["listingId"]) 
  . ' and Pretoken of: ' . $_GET["preToken"];
?>

<form action="authorize.php" method="post">
  <label>
    Favorite color (blue is correct):
  </label>
  <input type="text" value="blue">
  <button type="submit">
    OK, authorize me 
  </button>
</form>
