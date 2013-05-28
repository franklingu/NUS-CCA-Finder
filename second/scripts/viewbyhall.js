$(document).ready(function(){
    $('#slider').carousel({  
        interval: 2000 
    });

	$('#slider').mouseover(function(){
		$(this).carousel('pause');
	});

	$('#slider').mouseout(function(){
		$(this).carousel({
			interval: 2000
		})
	});

	$('#slide1').onclick(function(){
		var num = 0;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide2').onclick(function(){
		var num = 1;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide3').onclick(function(){
		var num = 2;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide4').onclick(function(){
		var num = 3;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide5').onclick(function(){
		var num = 4;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide6').onclick(function(){
		var num = 5;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide7').onclick(function(){
		var num = 6;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});
});