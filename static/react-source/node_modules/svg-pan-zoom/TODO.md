# TODO 

- uniwheel can be removed/moved
- controlicons can be removed/moved
- Think about server.js

## Alfa release
- Center/fit/contain/fill plugin
- Min/Max zoom plugin
- Controls plugin
- Mouse wheel plugin
- Documentation

# DONE

# Events
- `before:plugin:remove`
- `after:plugin:remove`
- *`panzoom`
- *`render`
- `before:destroy`
- There is no `after:destroy` as event system is removed at that point

## before:plugin:remove
`{name: pluginName}`

## after:plugin:remove 
`{name: pluginName}`

## panzoom 
`{x: 0, y: 0, zoom: 0}`
Event data alterable

## render 
`{x: 0, y: 0, zoom: 0}`
Event data alterable

## before:render 
_empty_

## after:render
_empty_

## before:destroy
`null`


# Namespaces
- __user
- __system
- pluginName
