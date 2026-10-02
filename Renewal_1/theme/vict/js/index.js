$(function(){
	$('.top_lnb_dep > a').click(function(){
		$(this).toggleClass('on');		
		$(this).parent().find('div').slideToggle();
	});
})


function Size_pc(){
	$('.header').on("mouseenter", function(){
		$('.header .dep2').stop().slideDown();
		$('.dep2_bg').stop().slideDown();
	}).on("mouseleave", function(){
		$('.header .dep2').stop().slideUp();
		$('.dep2_bg').stop().slideUp();
	});	
	
}

function Size_mobile(){
//	$('.main_wrap .section2').addClass('active');
	


}

$(window).load(function(){//사이트 최초 접속 시
	var screen_size = $(window).width();
	if(screen_size > 1024){
		
		Size_pc();
	}else{
		$('.header').off("mouseenter");
		Size_mobile();
	}
});




$(window).resize(function(){//사이즈 리사이징 시
	var screen_size = $(window).width();
	if(screen_size > 1024){
		Size_pc();
	}else{
		$('.header').off("mouseenter");
		Size_mobile();
	}
});




function goBack(){
	window.history.back();
}
$(document).ready(function(){
	$(".btn_back_script").bind("click",function(){
		goBack();
	});
});

function layerpopup2(names,url){
	var names = names;
	var pop_width = $(window).outerWidth();
	var pop_height = $(window).outerHeight();
	if(pop_width >= 600){
		pop_width = 600;
	}else if(pop_width < 600 && pop_width > 480){
		pop_width = $(window).width() - 50;
	}else if(pop_width <= 480){
		pop_width = $(window).width() - 50;
	}
	if(pop_height >= 600){
		pop_height = 400;
	}else if(pop_height < 600 && pop_height > 300){
		pop_height = $(window).height() - 50;
	}else if(pop_height <= 300){
		pop_height = $(window).height() - 50;
	}
	$(".layer_popup").dialog({
		resizable : false,
		width : pop_width,
		height : pop_height,
		dialogClass : false,
		modal : true,
		title : names,
		position : {
			my : "center center",
			at : "center center",
			of : window
		},
		open : function(event, ui){
			$("html").css({overflow : "hidden"});
			document.getElementById("lay_pop").innerHTML="<iframe src="+url+" id='uni_iframe'></iframe>";
		},
		beforeClose : function(event,ui){
			$("html").css({overflow : "inherit"});
		},
		show : {
			effect : "drop",
			duration : 800,
			direction : "up"
		},
		hide : {
			effect : "drop",
			duration : 800,
			direction : "up"
		}
	});
}


function layerpopup(names){
	var names = names;
	var pop_width = $(window).outerWidth();
	var pop_height = $(window).outerHeight();
	if(pop_width >= 600){
		pop_width = 600;
	}else if(pop_width < 600 && pop_width > 480){
		pop_width = $(window).width() - 50;
	}else if(pop_width <= 480){
		pop_width = $(window).width() - 50;
	}
	if(pop_height >= 600){
		pop_height = 400;
	}else if(pop_height < 600 && pop_height > 300){
		pop_height = $(window).height() - 50;
	}else if(pop_height <= 300){
		pop_height = $(window).height() - 50;
	}
	$(".layer_popup").dialog({
		resizable : false,
		width : pop_width,
		height : pop_height,
		dialogClass : false,
		modal : true,
		title : names,
		position : {
			my : "center center",
			at : "center center",
			of : window
		},
		open : function(event, ui){
			$("html").css({overflow : "hidden"});
		},
		beforeClose : function(event,ui){
			$("html").css({overflow : "inherit"});
		},
		show : {
			effect : "drop",
			duration : 800,
			direction : "up"
		},
		hide : {
			effect : "drop",
			duration : 800,
			direction : "up"
		}
	});
}



//메인스크립트


$(document).ready(function() {

	$('#fullpage').fullpage({
	//options here
		licenseKey: 'OPEN-SOURCE-GPLV3-LICENSE',
		autoScrolling:true,
		scrollHorizontally: true,
		navigation: true, 
		navigationPosition: 'right',
		normalScrollElements : '.pop_bg, .layer_box, .sitemap_wrap, intro' ,
		navigationTooltips: ['MAIN', 'MCNT1', 'MCNT2', 'MCNT3', 'FOOTER', ],
		responsiveWidth: 1024,
		scrollBar:true,
		afterLoad: function(anchorLink, index,section){
			
			
			//if(index.index == 4){
			//	$('.ft_bn_wrap').addClass('ft');
			//}else{
			//	$('.ft_bn_wrap').removeClass('ft');
			//}
		
		}
	});
	

});  




$(window).scroll(function(){
	var wah = $(this).scrollTop();
	if (0 < wah){
		$(".header").addClass("sc");
	} else {
		$(".header").removeClass("sc");

	}
});








