$(document).ready(function(){
    $('#slider').carousel({  
        interval: 100; 
    });

	$('#slider').hover(function(){
		$(this).carousel('pause');
	});

	$('#slide1').click(function(){
		var num = 0;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide2').click(function(){
		var num = 1;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide3').click(function(){
		var num = 2;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide4').click(function(){
		var num = 3;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide5').click(function(){
		var num = 4;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide6').click(function(){
		var num = 5;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});

	$('#slide7').click(function(){
		var num = 6;
		document.alert("does not work!");
		$('.carousel').carousel(num);
	});
});