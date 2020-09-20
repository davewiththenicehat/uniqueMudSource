var goldenlayout_config = {
    content: [{
        type: 'column',
        content: [{
            type: 'row',
            content: [{
                type: 'column',
                content: [{
                    type: 'component',
                    componentName: 'Main',
                    isClosable: false,
                    tooltip: 'Main - drag to desired position.',
                    componentState: {
                        cssClass: 'content',
                        types: 'untagged',
                        updateMethod: 'newlines',
                    },
                }, {
                    type: 'component',
                    componentName: 'input',
                    id: 'inputComponent',
                    height: 10,
                    isClosable: false,
                    tooltip: 'Input - The last input in the layout is always the default.',
                }]
            },{
                type: 'column',
                content: [{
                    type: 'component',
                    componentName: 'evennia',
                    componentId: 'evennia',
                    title: 'map',
                    height: 60,
                    isClosable: false,
                    componentState: {
                        types: 'map-pane',
                        updateMethod: 'newlines',
                    },
                }, {
                    type: 'component',
                    componentName: 'mycomponent',
                    componentId: 'audio-pane',
                    title: 'audio',
                    isClosable: false,
                    componentState: {
                        cssClass: 'content',
                        types: 'audio-pane',
                        updateMethod: 'newlines',
                    },
                }],
            }],
        }]
    }]
};