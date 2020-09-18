let myplugin = (function () {
    //
    //
    var postInit = function() {
        var myLayout = window.plugins['goldenlayout'].getGL();

//        myLayout.registerComponent( "mycomponent", function (container, componentState) {
//            let div = $("<div class='content'></div>");
//            initComponent(div, container, componentState, "all", "newlines");
//            container.on("destroy", calculateUntaggedTypes);
//        });

        // register our component and replace the default messagewindow
        myLayout.registerComponent( 'mycomponent', function (container, componentState) {
            let mycssdiv = $('<div>').addClass('myCSS');
            mycssdiv.attr('types', 'mytag');
            mycssdiv.attr('updateMethod', 'newlines');
            mycssdiv.appendTo( container.getElement() );
        });

        console.log("MyPlugin Initialized.");
    }

    return {
        init: function () {},
        postInit: postInit,
    }
})();
window.plugin_handler.add("myplugin", myplugin);
