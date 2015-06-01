<!DOCTYPE html>
<html>
    <head>
        <title>Reddit Images By Reddit User: {{user}}</title>
    </head>
    <body>
        <div id="pagebody">
            %	for comment in comments:
            	%for image in comment['images']:
					<a href="{{comment['permalink']}}"><img src={{image}}></a>
				%end
			%	end
			
        </div>
    </body>
</html>