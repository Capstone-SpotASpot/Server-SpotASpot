$(document).ready(function() {

    const successful_add_el = document.getElementById("form_success");
    const raw_success = successful_add_el.textContent;

    // remove new lines and spaces
    const success = raw_success.toString().replace(/^\s+|\s+$/g, '');

    if(success == "True")
    {
        display_alert();
    }
});


function display_alert()
{
    const page_url = window.location.href.toString();
    let form_type = ""

    // check if adding a car
    form_type = page_url.indexOf("car") != -1  ? "Car" : form_type;

    // check if adding a tag
    form_type = page_url.indexOf("tag") != -1  ? "Tag" : form_type;


    alert(`Successfully Added ${form_type}`);
}
