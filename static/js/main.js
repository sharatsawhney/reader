$(".navbar-toggle").click(function(){
	if($(".navbar").css('height') == '60px'){
		$(".navbar").css('height','380px');	
		var width = $(window).width();
		$(".navbar-nav li").attr('style','width:'+ width+ 'px !important');
	}else{
		$(".navbar").css('height','60px');	
	}
    
})

