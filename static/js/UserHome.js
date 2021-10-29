function todayDate(){
        var d = new Date();
        var n = d.getFullYear() + " ";
        return document.getElementById("date").innerHTML = n;
    }

    $(document).click(function(e){

        if (e.target.nodeName == 'H5'){
                window.open('static/files/' + e.target.innerText.replace("/","_") + '.pdf')
                }
            })

    $(function() {
        $.ajax({
            url: '/getWish',
            type: 'GET',
            success: function(res) {
                var div = $('<div>')
                .attr('class', 'list-group card shadow-sm')
                var div = $('<div>')
                .attr('class', 'card-body rounded bg-light')
                .append($('<a href="#">')
                    .attr('class', 'underlineHover list-group-item bg-light shadow')
                    .append($('<h5>')
                        .attr('class', 'card-header rounded'),
                        $('<h6>')
                        .attr('class', 'list-group-item-text'),
                        $('<li>')
                        .attr('class', 'list-group-item-text'),
                        $('<p>')
                        .attr('class', 'card-subtitle mb-2 text-muted')));
                var wishObj = JSON.parse(res);
				var wish = '';

				$.each(wishObj,function(index, value){
					wish = $(div).clone();
					$(wish).find('h5').text(value.Short_Title);
					$(wish).find('h6').text(value.Title);
					$(wish).find('li').text(value.Stage);
					$(wish).find('p').text(value.Date);
					$('.jumbotron').append(wish);
                        });
                    },
                        error: function(error) {
                            console.log(error);
                    }
        });
    });