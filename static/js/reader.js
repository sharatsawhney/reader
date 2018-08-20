if ($(window).width() < 1220) {
   $(".reader").css('display','none');
   $("#wrapper").css('display','none');
}
else {
   $(".reader-small").css('display','none');
   $(".rs-nav").css('display','none');
}
var numberOfPages = $("#hiddenpages").html();
var lastpage = $("#hiddenlastpage").html();
$(window).ready(function() {
		$('#magazine').turn({
							display: 'double',
							pages: numberOfPages,
							acceleration: true,
							gradients: !$.isTouch,
							elevation:50,
							when: {
								turned: function(e, page) {
									$('#page-number').val(page);
									$("#pageRange").val(page);
                                    var el = $("#pageRange");
                                    var width = el.width();
			                        var newPoint = (el.val() - el.attr("min")) / (el.attr("max") - el.attr("min"));
			                        var offset = -1.3;
			                        if (newPoint < 0) { newPlace = 0; }
									else if (newPoint > 1) { newPlace = width; }
            						else { newPlace = width * newPoint + offset; offset -= newPoint; }
						            el
								     .next("output")
								     .css({
								       left: newPlace + 428,
								       marginLeft: offset + "%"
								     })
								     .text(el.val());
								}
							}
		});
		if(lastpage != 'False'){
		    $("#page-number").val(lastpage);
		    $('#magazine').turn('page', $('#page-number').val());
		}

		$('#number-pages').html(numberOfPages);

		$('#page-number').keydown(function(e){

			if (e.keyCode==13)
				$('#magazine').turn('page', $('#page-number').val());
				
		});

        $('.bottom-pane output').text($("#pageRange").val());
		$('.bottom-pane output').css('left','428px');
		$('#pageRange').on('input',function(){
			$("#magazine").turn('page',$("#pageRange").val());
			var el = $(this);
			var width = el.width();
			var newPoint = (el.val() - el.attr("min")) / (el.attr("max") - el.attr("min"));
			var offset = -1.3;
			if (newPoint < 0) { newPlace = 0; }
            else if (newPoint > 1) { newPlace = width; }
            else { newPlace = width * newPoint + offset; offset -= newPoint; }

            el
		     .next("output")
		     .css({
		       left: newPlace + 428,
		       marginLeft: offset + "%"
		     })
		     .text(el.val());
        })

         /*$("#magazine").click(function(){
        	$('#myModal').modal('hide');
            $("#myModal").remove();
        	$('body').prepend('<div class="modal" id="myModal" role="dialog"><div class="modal-dialog"><div class="modal-content"><div class="modal-body"></div></div></div></div>')
            $(".modal-body").append($(this).find('.turn-page').clone());
            $(".modal-body #magazine .turn-page").css('background-size','100% 80%');
            $(".modal-body #magazine .turn-page").css('background-repeat','no-repeat');
            $(".modal-body #magazine .turn-page").css('background-position','center');
            $(".modal-body #magazine .turn-page").css('position','absolute');
            $(".modal-body #magazine .turn-page").css('width','100%');
            $(".modal-body #magazine .turn-page").css('height','100%');
            $(".modal-body #magazine .turn-page").css('margin-left','-30%');
            $(".modal-body #magazine .turn-page").css('margin-top','-10%');
            $('#myModal').modal('show');
        	
        }) */
        var mag = false;
        $("#magazine").click(function(){
        	if(mag==false){
	        	$(this).animate({'zoom':1.3},1);
	        	$(this).css('position','absolute');
	        	$(this).css('width','90%');
	            $(this).css('margin-left','-25%');
	            $(this).css('margin-top','-1%');
	            $(this).css('height','110%');
	            $('body').css('overflow','scroll');
	            $('.bottom-pane').css('display','none');
	            $('#wrapper').css('display','none');
	            $('.reader').css('background-color','#F2F2F2');
	            $('.reader').css('box-shadow','none');
	            mag = true;
            }else{
            	$(this).animate({'zoom':1},1);
            	$(this).css('position','relative');
            	$(this).css('width','100%');
	            $(this).css('margin-left','0%');
	            $(this).css('margin-top','0%');
	            $(this).css('height','100%');
	            $('body').css('overflow','hidden');
	            $('.bottom-pane').css('display','block');
	            $('#wrapper').css('display','block');
	            $('.reader').css('background-color','white');
	            $('.reader').css('box-shadow','0px 3px 16px #888888');
	            mag = false;
            }
        })


     


	});
	



	$(window).bind('keydown', function(e){
		
		if (e.keyCode==37)
			$('#magazine').turn('previous');
		else if (e.keyCode==39)
			$('#magazine').turn('next');
			
	});
function getlength(number) {
    return number.toString().length;
}

var pages = $("#hiddenpages").html();
var id = $("#hiddenid").html();
var digit = getlength(pages);
var pagesaccess = $("#hiddenpagesaccess").html();


for(var i=1;i<=pages;i++){
	var ireplacer = i;
	if(digit==2){
		if(i<10){
		    i = "0" + i;
		}
	}
	else if(digit==3){
		if(i<10){
			i = "00" + i;
		}else if(i>=10 && i<100){
			i = "0" + i;
		}
	}
    else if(digit=4){
    	if(i<10){
    		i="000" + i;
    	}else if(i>=10 && i<100){
    		i = "00" + i;
    	}else if(i>=100 && i<1000){
    		i = "0" + i;
    	}
    }
    if(ireplacer<=pagesaccess){
		$("#magazine").append("<div style='background-image:url(https://s3.ap-south-1.amazonaws.com/readerearth/static/" + id + "/" + id + "-" + i + ".jpg);'></div>");
		$(".reader-small").append("<div style='background-image:url(https://s3.ap-south-1.amazonaws.com/readerearth/static/" + id + "/" + id + "-" + i + ".jpg)' class='rsdiv'></div>");
	}
}

$("#nighttoggle").click(function(){
	var color = $("body").css('background-color');
	if(color == "rgb(204, 204, 204)"){
		$("body").css('background-color',"#333333");
	}else if(color == "rgb(51, 51, 51)"){
		$("body").css('background-color','#ccc');
	}
})



$(".newtextnotes").on('input',function(){
	$("#newnotessave").html('Saving Changes...')
	setTimeout(function(){ 
        var title = $("#titlenotes").val();
		var text = $(".newtextnotes").val();
		var pageNumber = $("#pageRange").val();
		if(title!='' && text!=''){
			$.ajax({
					url: '/add_notes/',
					type:'POST',
					data:
					{
						'title': title,
						'text': text,
						'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
					},
					success: function(data)
					{
					   $("#oldpaper").html(data);
					   $.ajax({
							url: '/save_page/',
							type:'POST',
							data:
							{
								'ebookid': id,
								'page': pageNumber,
								'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
							},
							success: function(data)
							{                   
							    $("#newnotessave").html('Changes Saved!')

							},
							error: function(xhr,status,error){
							alert(xhr.responseText);
						    }             
						});
					},
					error: function(xhr,status,error){
					alert(xhr.responseText);
				    }             
				});
	    }
	 }, 500);
})

$(".othertextnotes").on('input',function(){
	var elem = $(this);
	elem.parent().parent().parent().find(".othernotessave").html('Saving Changes...')
	setTimeout(function(){ 
		var classlist = elem.attr('class').split(' ');
		if(classlist[0] != 'othertextnotes'){
			var mainclass = classlist[0];
		}else{
			var mainclass = classlist[1];
		}
		var mainclassid = mainclass.substr(14);
		var titleid = $("#othertitlenotes" + mainclassid).html();
        var title = titleid;
		var text = elem.val();
		var pageNumber = $("#pageRange").val();
		if(title!='' && text!=''){
			$.ajax({
					url: '/add_notes/',
					type:'POST',
					data:
					{
						'title': title,
						'text': text,
						'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
					},
					success: function(data)
					{
					   $.ajax({
							url: '/save_page/',
							type:'POST',
							data:
							{
								'ebookid': id,
								'page': pageNumber,
								'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
							},
							success: function(data)
							{
							   elem.parent().parent().parent().find(".othernotessave").html('Changes Saved!')
				               
							},
							error: function(xhr,status,error){
							alert(xhr.responseText);
						    }             
						});
					},
					error: function(xhr,status,error){
					alert(xhr.responseText);
				    }             
				});
	    }
	 }, 500);
})



$("#oldpaper").hide();
$("#musiclist").hide();
$(".onotesbtn").click(function(){
	$("#paper").hide();
	$("#musiclist").hide();
	$("#oldpaper").show();
    $(".nnotesbtn").removeClass('active');
	$(".lmusicbtn").removeClass('active');
	$(".onotesbtn").addClass('active');
})

$(".lmusicbtn").click(function(){
	$("#paper").hide();
	$("#oldpaper").hide();
	$("#musiclist").show();
	$(".nnotesbtn").removeClass('active');
	$(".lmusicbtn").addClass('active');
	$(".oldnotesbtn").removeClass('active');
})
$(".nnotesbtn").click(function(){
	$("#oldpaper").hide();
	$("#musiclist").hide();
	$("#paper").show();
	$(".nnotesbtn").addClass('active');
	$(".lmusicbtn").removeClass('active');
	$(".oldnotesbtn").removeClass('active');
})
