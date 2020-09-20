let myplugin = (function () {
    //
    //
    var postInit = function() {
        var myLayout = window.plugins['goldenlayout'].getGL();

        // register our component and replace the default messagewindow
        myLayout.registerComponent( 'mycomponent', function (container, componentState) {
            let mycssdiv = $('<div>').addClass('content myCSS');
            mycssdiv.attr('types', 'mytag1 mytag2');
            mycssdiv.attr('updateMethod', 'newlines');
            mycssdiv.appendTo( container.getElement() );
            container.on("tab", plugins['goldenlayout'].onTabCreate);
        });

        console.log("MyPlugin Initialized.");
    }

    return {
        init: function () {},
        postInit: postInit,
    }
})();
window.plugin_handler.add("myplugin", myplugin);
