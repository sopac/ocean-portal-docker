var ocean = ocean || {};

$(document).ready(function(){
    $(".alert-info").alert("close");
});  

$("div.app").click(function(e) {
    if(e.target != this) return;
    var classNames = this.classList;
    if($.inArray("dev", classNames) > -1) {
        $("div.info").empty();
        $("div.info").append('<div class="alert alert-info alert-dismissible" role="alert"><button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><strong>Heads up!</strong> This application is coming soon.</div>');
        return;
    }
    window.location = "app.html#" + this.id;
    ocean.app = {"new": this.id, "old": ocean.app};
    return false;
});

$('a.app').click(function(e) {
    window.location = "app.html";
    window.location = "app.html#" + this.id;
    ocean.app = {"new": this.id, "old": ocean.app};
    return false;
});
