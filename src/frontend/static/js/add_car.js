$(document).ready(function() {

    const successful_add_el = document.getElementById("successful-car-add-val");
    const raw_success_add = successful_add_el.textContent;

    // remove new lines and spaces
    const successful_add = raw_success_add.toString().replace(/^\s+|\s+$/g, '');

    if(successful_add == "True")
    {
        added_car();
    }
});


function added_car()
{
    alert("Car Added Successfully");
}
