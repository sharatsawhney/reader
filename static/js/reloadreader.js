function readerload(readerheight){
$(".selector-div").hide();
  var esource = $("#hidden-esource").html();
  $("#rangeSlider").remove();
  var controls = document.getElementById("control");
  var currentPage = document.getElementById("current-percent");
  var slider = document.createElement("input");
  var slide = function(){
      var cfi = book.locations.cfiFromPercentage(slider.value / 100);
      
      rendition.display(cfi);
      $("#rangeSlider").blur();
  };
  var mouseDown = false;
  var params = URLSearchParams && new URLSearchParams(document.location.search.substring(1));
  var url = params && params.get("url") && decodeURIComponent(params.get("url"));
  var currentSectionIndex = (params && params.get("loc")) ? params.get("loc") : undefined;

  // Load the opf
  esource = "https://s3.ap-south-1.amazonaws.com/readerearth/" +  esource;
  book = ePub('/media/epubs/1.epub');
  rendition = book.renderTo("viewer", {
    width: "100%",
    height: readerheight,
    spread: 'auto',
  });
  var displayed = rendition.display();
  var title = document.getElementById("title");
  rendition.display(currentSectionIndex);
  rendition.themes.override("font-family", "Arial",true);
  rendition.themes.override("text-align","left",true);
  rendition.themes.override('height','800px');
  /*rendition.themes.register("night", { "body": { "background": "#191919","color": "white"}});
  rendition.themes.select("night");
  $("body").css('background-color','#191919');*/
  for(var i=0;i<highlightarr.length;i++){
      rendition.annotations.highlight(highlightarr[i],String(highlightcolorarr[i]) + '@#$%^-decode##' + String(highlighttextarr[i]));
  }
  
  book.ready.then(function(){
    function doSearch(q) {
      return Promise.all(
          book.spine.spineItems.map(item => item.load(book.load.bind(book)).then(item.find.bind(item, q)).finally(item.unload.bind(item)))
      ).then(results => Promise.resolve([].concat.apply([], results)));
    };


    $("#reader-search i").click(function(){
      var term = $("#reader-search-input").val();
      if(term.length >1){
        $('.reader-search-results-main').html('');
        doSearch(term).then(function(results){
          $(".reader-search-results").show();
          dialogopen = true;
          $("#reader-search-number").html(results.length);
          var searchlength = term.length
          for(var i in results){
            var searchindex = results[i].excerpt.toLowerCase().indexOf(term);

            let result = '<div class="reader-search-item" data-link="'+results[i].cfi+'"><div class="reader-search-item-content">' + results[i].excerpt.substring(0,searchindex)+ '<span class="reader-search-highlight">' +results[i].excerpt.substring(searchindex,searchindex+searchlength) + '</span>' + results[i].excerpt.substring(searchindex+searchlength) + '</div><div class="reader-search-item-location">'+book.locations.locationFromCfi(results[i].cfi) +'</div></div>'
            $('.reader-search-results-main').append(result);

          }
        })
    }
    });
    
    $(document).keypress(function(e) {
        if(e.which == 13 && $("#reader-search-input").is(":focus")) {
            var term = $("#reader-search-input").val();
            if(term.length >1){
              $('.reader-search-results-main').html('');
              doSearch(term).then(function(results){
                $(".reader-search-results").show();
                dialogopen = true;
                $("#reader-search-number").html(results.length);
                var searchlength = term.length
                for(var i in results){
                  var searchindex = results[i].excerpt.toLowerCase().indexOf(term);

                  let result = '<div class="reader-search-item" data-link="'+results[i].cfi+'"><div class="reader-search-item-content">' + results[i].excerpt.substring(0,searchindex)+ '<span class="reader-search-highlight">' +results[i].excerpt.substring(searchindex,searchindex+searchlength) + '</span>' + results[i].excerpt.substring(searchindex+searchlength) + '</div><div class="reader-search-item-location">'+book.locations.locationFromCfi(results[i].cfi) +'</div></div>'
                  $('.reader-search-results-main').append(result);

                }
              })
          }
        }
    });

    $(document).dblclick(function(e){
    	window.getSelection().empty();
    });
    
    var next = document.getElementById("next");

    next.addEventListener("click", function(e){
      book.package.metadata.direction === "rtl" ? rendition.prev() : rendition.next();
      var percentage = $("#rangeSlider").val();
      $("#rangeSlider").css('background','linear-gradient(to right, #7e71c9 '+ percentage +'%, rgb(230,230,230) '+ 0 + '%)');
      e.preventDefault();
    }, false);

    var prev = document.getElementById("prev");
    prev.addEventListener("click", function(e){
      book.package.metadata.direction === "rtl" ? rendition.next() : rendition.prev();
      var percentage = $("#rangeSlider").val();
      $("#rangeSlider").css('background','linear-gradient(to right, #7e71c9 '+ percentage +'%, rgb(230,230,230) '+ 0 + '%)');
      e.preventDefault();
    }, false);

    var keyListener = function(e){

      // Left Key
      if ((e.keyCode || e.which) == 37) {
        book.package.metadata.direction === "rtl" ? rendition.next() : rendition.prev();
          var percentage = $("#rangeSlider").val();
          $("#rangeSlider").css('background','linear-gradient(to right, #7e71c9 '+ percentage +'%, rgb(230,230,230) '+ 0 + '%)');
      }

      // Right Key
      if ((e.keyCode || e.which) == 39) {
        book.package.metadata.direction === "rtl" ? rendition.prev() : rendition.next();
          var percentage = $("#rangeSlider").val();
          $("#rangeSlider").css('background','linear-gradient(to right, #7e71c9 '+ percentage +'%, rgb(230,230,230) '+ 0 + '%)');
      }

    };

    rendition.on("keyup", keyListener);
    document.addEventListener("keyup", keyListener, false);
    
    // Load in stored locations from json or local storage
    var key = book.key()+'-locations';
    var stored = localStorage.getItem(key);
    if (stored) {
       return book.locations.load(stored);
    } else {
      // Or generate the locations on the fly
      // Can pass an option number of chars to break sections by
      // default is 150 chars
      return book.locations.generate(1600);
    }

  })
  .then(function(locations){
  	var bookmarkappender = ``;
  	for(var i in bookmarkarr){
      	var bookmarkcfi = book.locations.cfiFromLocation(parseInt(bookmarkarr[i]));
      	if(bookmarkdataarr[i].length > 25){
      		bookmarkdataarr[i] = bookmarkdataarr[i].substring(0,25) + '...';
      	}
      	var obj = `<li class="bookmark-li" data-cfi="` + bookmarkcfi + `"><span class="bookmark-data">` + bookmarkdataarr[i] + `</span><span class="bookmark-loc">` + bookmarkarr[i] +`</span></li>`;
      	bookmarkappender = bookmarkappender + obj;
      }
     bookmarkappender = `<ul class="bookmark-ul">` + bookmarkappender + `</ul>`;
    $("#bookmark-menu").append(bookmarkappender);
      var noteappender = ``;
  	for(var i in notetextarr){
      	var noteloc = book.locations.locationFromCfi(notecfiarr[i]);
      	var truenotetext = notetextarr[i];
      	var truenoteselectedtext = noteselectedtextarr[i];
      	if(notetextarr[i].length > 25){
      		notetextarr[i] = notetextarr[i].substring(0,25) + '...';
      	}
      	if(noteselectedtextarr[i].length > 60){
      		noteselectedtextarr[i] = noteselectedtextarr[i].substring(0,60) + '...';
      	}
      	var obj = `<div class="reader-notes-item" data-cfi="` + notecfiarr[i] + `" data-note="` + truenotetext + `" data-text="` + truenoteselectedtext + `"><div class="reader-notes-club-div">
        	           <div class="reader-notes-note">` + notetextarr[i] + `</div>
        	           <div class="reader-notes-text">` + noteselectedtextarr[i] + `</div></div>
        	           <svg class="reader-notetick-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14.28 14.28"><title>Tick</title><circle cx="7.14" cy="7.14" r="7.14" fill="#999"/><rect x="7.89" y="3.23" width="1.15" height="7.94" transform="translate(7.57 -3.88) rotate(45)" fill="#fff"/><rect x="4.41" y="6.5" width="1.16" height="4.13" transform="translate(-4.6 6.04) rotate(-45)" fill="#fff"/></svg>
        	           <div class="reader-notes-loc">`+ noteloc +`</div>
                     </div>`;
      	noteappender = noteappender + obj;
      };

    $("#reader-notes-list").append(noteappender);
      controls.style.display = "block";
      slider.setAttribute("type", "range");
      slider.setAttribute("min", 0);
      slider.setAttribute("id", 'rangeSlider');
      slider.setAttribute("max", 100);
      // slider.setAttribute("max", book.locations.total+1);
      slider.setAttribute("step", 1);
      slider.setAttribute("value", 0);

      slider.addEventListener("change", slide, false);
      slider.addEventListener("input",function(){
          var percentage = $("#rangeSlider").val();
          $("#rangeSlider").css('background','linear-gradient(to right, #7e71c9 '+ percentage +'%, rgb(230,230,230) '+ 0 + '%)');
          $("#reader-current-percentage").html(percentage + "%");
          $("#reader-total-locations").html(locations.length);
          $("#reader-current-location").html(Math.floor(locations.length*percentage*0.01)+ '-' + Math.ceil(locations.length*percentage*0.01) + '/');
      });
      slider.addEventListener("mousedown", function(){
          mouseDown = true;
      }, false);
      slider.addEventListener("mouseup", function(){
          mouseDown = false;
      }, false);
      
      // Wait for book to be rendered to get current page
      displayed.then(function(){
          // Get the current CFI
          var currentLocation = rendition.currentLocation();
          // Get the Percentage (or location) from that CFI
          var currentPage = book.locations.percentageFromCfi(currentLocation.start.cfi);
          slider.value = currentPage;
          currentPage.value = currentPage;
          var percentage = 0;
          $("#rangeSlider").css('background','linear-gradient(to right, #7e71c9 '+ percentage +'%, rgb(230,230,230) '+ 0 + '%)');
      });

      controls.appendChild(slider);
      currentPage.addEventListener("change", function(){
        var cfi = book.locations.cfiFromPercentage(currentPage.value/100);
        rendition.display(cfi);
      }, false);
      var relocatedcount = 0;
      // Listen for location changed event, get percentage from CFI
      rendition.on('relocated', function(location){
          relocatedcount = relocatedcount + 1;
          var percent = book.locations.percentageFromCfi(location.start.cfi);
          var percentage = Math.round(percent * 100);
          if(!mouseDown) {
              slider.value = percentage;
              var percenti = $("#rangeSlider").val();
              $("#rangeSlider").css('background','linear-gradient(to right, #7e71c9 '+ percenti +'%, rgb(230,230,230) '+ 0 + '%)');
          }
          currentPage.value = percentage;
          $("#reader-current-percentage").html(percentage + "%");
          $("#reader-total-locations").html(locations.length);
          $("#reader-current-location").html(location.start.location+ '-' + location.end.location + '/');
          if($.inArray(parseInt(location.start.location),bookmarkarr) != -1){
            $("#reader-bookmark-svg path").css({fill:'#7e71c9'});
          }else{
            $("#reader-bookmark-svg path").css({fill:'#999'});
          }
          if(percentage>=50 && ratingbox == 1){
            ratingbox = 0;
            $(".reader-reviews").show();
            rendition.themes.register("opaque", { "body": { "opacity": "0.1"}});
            rendition.themes.select("opaque");
          }
          elcfi = location.start.cfi;
          if(relocatedcount != 1 && relocatedcount != 2){
            var prVar = setInterval(prTimer, 1000);
            var prcounter = 0;
            function prTimer() {
              prcounter = prcounter + 1;
              if(prcounter == 8){
                  var loccur = $("#reader-current-location").html().substring(0,$("#reader-current-location").html().length-1);
                  var loccur1 = parseInt(loccur.substring(0,loccur.indexOf('-')));
                  var loccur2 = parseInt(loccur.substring(loccur.indexOf('-')+1,loccur.length));
                  var loctotal = parseInt($("#reader-total-locations").html());
                  $.ajax({
                  url: '/save_percent/',
                  type:'POST',
                  data:
                  {
                    'loccur1':loccur1,
                    'loccur2':loccur2,
                    'loctotal':loctotal,
                    'ebookid': parseInt($("#hidden-ebook-id").html()),
                    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
                  },
                  success: function(data)
                  {
                    clearInterval(prVar);
                  },
                  error: function(xhr,status,error){
                      alert(xhr.responseText);
                    }             
                });
              }
            }
          }
      });

      /*rendition.on("selected", function(cfiRange, contents) {
        rendition.annotations.highlight(cfiRange, {}, (e) => {
          console.log("highlight clicked", e.target);
        });
        contents.window.getSelection().removeAllRanges();

      });*/
      /*function onMouseUp(e) {
          var selection = book.renderer.render.window.getSelection();
          var text = selection.toString();
          console.log("Texto selecionado: %s", text);
          // $('body #area').highlight(text);
      }
    
      book.on('renderer:mouseup', onMouseUp);*/

      var epubcfi = undefined;
      var newcfi = undefined;
      var useselection = undefined;
      var selected = undefined;
      rendition.on('mouseup',function(cfiRange,contents){
        epubcfi = undefined;
        newcfi = undefined;
        var range = rendition.getRange(rendition.currentLocation().start.cfi);
        var endRange = rendition.getRange(rendition.currentLocation().end.cfi);
        range.setEnd(endRange.startContainer, endRange.startOffset);
        var cfistring = range.toString();
        var selection =  rendition.views()._views[0].iframe;
        var idoc= selection.contentDocument || selection.contentWindow.document;
        var iwin= selection.contentWindow || selection.contentDocument.defaultView;

        selected = ''+iwin.getSelection();
        if(selected.length > 0 && selected.replace(/\s+/g, '').length > 0){
            useselection = iwin.getSelection();
            var irange = iwin.getSelection().getRangeAt(0);
            var startcon = irange.startContainer.data;
            var paraindex = cfistring.indexOf(startcon);
            var selectionindex = irange.startOffset;
            
            var attacher = rendition.currentLocation().start.cfi.substring(8,rendition.currentLocation().start.cfi.indexOf('!'));
            epubcfi = new ePub.CFI(irange).toString();
            newcfi = epubcfi.substring(0,8) + attacher + epubcfi.substring(9,);
            var screenx = String(cfiRange.screenX-80) + 'px';
            var screeny = String(cfiRange.screenY-70) + 'px';
            var wwidth = $(window).width();
	      var wheight = $(window).height();
	      if(wheight - cfiRange.screenY-70 <= 0){
	      	screeny  = String(wheight - 120) + 'px';
	      }
	      if(wwidth - cfiRange.screenX-80 <= 0){
	      	screenx = String(wwidth-120) + 'px';
	      }
	      console.log(wwidth);
	      console.log(wheight);
	      console.log(screenx);
	      console.log(screeny);
            if(selected.indexOf(' ') != -1 && selected.indexOf(' ') != selected.length - 1){
                $(".selector-div").show();
                $(".selector-div").css({'top':screeny,'left': screenx});
            }else{
            	  $(".loading-dict-div").show();
            	  $(".dictionary-div").empty();
            	  $.ajax({
	              url: '/getdict/',
	              type:'POST',
	              data:
	              {
	                'word': selected,
	                'lang': $("#hidden-ebook-lang").html(),
	                'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
	              },
	              success: function(data)
	              {
	              	/*<div class="dictionary-pronunciation">θɪn</div>
					<div class="dictionary-part-of-speech">adjective</div>
					<table class="dictionary-definitions">
						<tbody>
							<tr><td class="dictionary-index"><strong>1</strong></td><td class="dictionary-definition">with opposite surfaces or sides that are close or relatively close together.</td></tr>
							<tr><th></th><td>
								<div class="dictionary-synonyms">
									<table><tbody>
										<tr><td class="dictionary-synonym-label">synonyms:</td><td>narrow, fine, implausible</td></tr>
									</tbody></table>
								</div>
							</td></tr>
						</tbody>
					</table>*/
					var phoneticlist = data['phoneticlist'];
	                var categorylist = data['categorylist'];
	                var definelist = data['definelist'];
	                var syarray = data['syarray'];
	                if(categorylist.length != 0){
	                	var appender = ``;
                          for(var i in categorylist){
                            var rowarray = ``;
                          for(var j in definelist[i]){
                          	var index = parseInt(j) + 1;
                          	var obj = `<tr><td class="dictionary-index"><strong>` + String(index) + `</strong></td><td class="dictionary-definition">` + definelist[i][j] + `</td></tr>`;
                          	rowarray = rowarray + obj;
                          };
                          if(syarray[i].length != 0){
                          	var systr = ``;
                          	for(var k in syarray[i]){
                                for(var m in syarray[i][k]){
                                	systr = systr + syarray[i][k][m] + `, `;
                                }
                          	}
                          	systr = `<tr><th></th><td>
								      <div class="dictionary-synonyms">
									  <table><tbody>
										<tr><td class="dictionary-synonym-label">synonyms:</td><td>` + systr +`</td></tr>
									  </tbody></table>
								      </div>
							          </td></tr>`
                          }else{
                          	var systr = ``;
                          }
                          var capp = `<div class="dictionary-pronunciation">` + phoneticlist[i] + `</div>
					                  <div class="dictionary-part-of-speech">` + categorylist[i] + `</div>
					                  <table class="dictionary-definitions">
						              <tbody>` + rowarray + systr + 
						              `</tbody>
					                  </table>`;
                          appender = appender + capp;
		                } 
		                appender = `<div class="dictionary-title">` + selected + `</div>` + appender;
		                $(".dictionary-div").append(appender);
		                $(".loading-dict-div").hide();
		                $('.dictionary-div').show();
		                $(".selector-div").show();
	                }else{
	                	$(".dictionary-div").append('Nothing to show!');
		                $(".loading-dict-div").hide();
		                $('.dictionary-div').show();
		                $(".selector-div").show();
	                }
	              },
	              error: function(xhr,status,error){
	                  alert(xhr.responseText);
	                }             
	          });
                var wwidth = $(window).width();
	          var wheight = $(window).height();
	          if(cfiRange.screenY +300 < wheight && cfiRange.screenX +387 < wwidth){
	            $(".dictionary-div").css({'top':cfiRange.screenY-100,'left':cfiRange.screenX-90});
	            $(".selector-div").css({'top':cfiRange.screenY-100+10,'left':cfiRange.screenX-90+290});
	          }else if(cfiRange.screenY +300>= wheight || cfiRange.screenX + 387>= wwidth){
	              if(cfiRange.screenY + 300 >= wheight && cfiRange.screenX + 387 < wwidth){
	                  var ydiff = cfiRange.screenY + 300- wheight;
	                  $(".dictionary-div").css({'top':cfiRange.screenY-ydiff -100,'left':cfiRange.screenX-90});
	                  $(".selector-div").css({'top':cfiRange.screenY-ydiff -100+10,'left':cfiRange.screenX-90+290});
	              }else if(cfiRange.screenY + 300 < wheight && cfiRange.screenX + 387 >= wwidth){
	                  var xdiff = cfiRange.screenX + 387 - wwidth;
	                  $(".dictionary-div").css({'top':cfiRange.screenY-100,'left':cfiRange.screenX-xdiff-90});
	                  $(".selector-div").css({'top':cfiRange.screenY-100+10,'left':cfiRange.screenX-xdiff-90+290});
	              }else if(cfiRange.screenY + 300 >= wheight && cfiRange.screenX + 387 >= wwidth){
	                  var xdiff = cfiRange.screenX + 387 - wwidth;
	                  var ydiff = cfiRange.screenY + 300- wheight;
	                  $(".dictionary-div").css({'top':cfiRange.screenY-ydiff-100,'left':cfiRange.screenX-xdiff-90});
	                  $(".selector-div").css({'top':cfiRange.screenY-ydiff-100+10,'left':cfiRange.screenX-xdiff-90+290});
	              }
	              
	          };
            }
        }
      });

      rendition.on('mousemove',function(){
          $(".hmarker-div").hide();
      });
      $(".hmarker-delete").click(function(){
          var cfirange = $(this).parent().attr('data-cfi');
          $.ajax({
            url: '/removehighlight/',
            type:'POST',
            data:
            {
              'ebookid': parseInt($("#hidden-ebook-id").html()),
              'cfirange': cfirange,
              'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data)
            {
              rendition.annotations.remove(cfirange,"highlight");
              $(".hmarker-note").html('');
              $(".note-textarea").val('');
              $(".hmarker-div").hide();
            },
            error: function(xhr,status,error){
                alert(xhr.responseText);
              }             
          });
      });
      var hmarkercfi = undefined;
      var hmarkercolor = undefined;
      var newnote = false;
      $(".hmarker-edit").click(function(e){
      	newnote = false;
          hmarkercfi = $(".hmarker-div").attr('data-cfi');
          $(".hmarker-div").hide();
          $(".note-maker").show();
          var wwidth = $(window).width();
          var wheight = $(window).height();
          if(e.screenY +195 < wheight && e.screenX + 380 < wwidth){
            $(".note-maker").css({'top':e.screenY-100,'left':e.screenX-90});
          }else if(e.screenY +195>= wheight || e.screenX + 380>= wwidth){
            if(e.screenY + 195 >= wheight && e.screenX + 380 < wwidth){
                var ydiff = e.screenY + 195- wheight;
                $(".note-maker").css({'top':e.screenY-ydiff -100,'left':e.screenX-90});
            }else if(e.screenY + 195 < wheight && e.screenX + 380 >= wwidth){
                var xdiff = e.screenX + 380 - wwidth;
                $(".note-maker").css({'top':e.screenY-100,'left':e.screenX-xdiff-90});
            }else if(e.screenY + 195 >= wheight && e.screenX + 380 >= wwidth){
                var xdiff = e.screenX + 380 - wwidth;
                var ydiff = e.screenY + 195- wheight;
                $(".note-maker").css({'top':e.screenY-ydiff-100,'left':e.screenX-xdiff-90});
            }
            
          }
          $(".note-control div").css('cssText','border:1px solid #999 !important');
          $(".note-highlighter1").css('cssText','border:2px solid #999 !important');
          hmarkercolor = 'rgb(255, 237, 165)';
          $(".note-textarea").val($(".hmarker-note").attr('data-text'));
      });
      $(".note-highlighter1").click(function(){
        $(".note-control div").css('cssText','border:1px solid #999 !important');
        $(".note-highlighter1").css('cssText','border:2px solid #999 !important');
        hmarkercolor = 'rgb(255, 237, 165)';
      });
      $(".note-highlighter2").click(function(){
        $(".note-control div").css('cssText','border:1px solid #999 !important');
        $(".note-highlighter2").css('cssText','border:2px solid #999 !important');
        hmarkercolor = 'rgb(219, 255, 183)';
      });
      $(".note-highlighter3").click(function(){
        $(".note-control div").css('cssText','border:1px solid #999 !important');
        $(".note-highlighter3").css('cssText','border:2px solid #999 !important');
        hmarkercolor = 'rgb(255, 219, 219)';
      });
      $(".note-highlighter4").click(function(){
        $(".note-control div").css('cssText','border:1px solid #999 !important');
        $(".note-highlighter4").css('cssText','border:2px solid #999 !important');
        hmarkercolor = 'rgb(201, 237, 237)';
      });
      $(".note-cancel").click(function(){
        $(".note-maker").hide();
      });
      $(".note-save").click(function(){
      	try{
      	    useselection.removeAllRanges();
      	}
      	catch(err){
              
      	}
          var notetext = $(".note-textarea").val();
          if(notetext == ''){
            var notenote = 0;
          }else{
            var notenote = 1;
          }
          if(newnote== true){
            var cf = newcfi;
            var cl = hmarkercolor;
            var seltext = selected;
          }else{
            var cf = hmarkercfi;
            var cl = hmarkercolor;
            var seltext = '';
          }

          $.ajax({
            url: '/changehighlight/',
            type:'POST',
            data:
            {
              'ebookid': parseInt($("#hidden-ebook-id").html()),
              'cfirange': cf,
              'notenote': notenote,
              'notetext':notetext,
              'color': cl,
              'selected':seltext,
              'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data)
            {
              $(".note-maker").hide();
              if(newnote==false){
                  rendition.annotations.remove(hmarkercfi,'highlight');
              }
              rendition.annotations.highlight(cf,String(cl) + '@#$%^-decode##' + String(notetext));
              if(newnote== true){
              	var noteappender = ``;
		      	var noteloc = book.locations.locationFromCfi(cf);
		      	var truenotetext = notetext;
		      	var truenoteselectedtext = seltext;
		      	if(notetext.length > 25){
		      		notetext = notetext.substring(0,25) + '...';
		      	}
		      	if(seltext.length > 60){
		      		seltext = seltext.substring(0,60) + '...';
		      	}
		      	var obj = `<div class="reader-notes-item" data-cfi="` + cf + `" data-note="` + truenotetext + `" data-text="` + truenoteselectedtext + `"><div class="reader-notes-club-div">
	          	           <div class="reader-notes-note">` + notetext + `</div>
	          	           <div class="reader-notes-text">` + seltext + `</div></div>
	          	           <svg class="reader-notetick-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14.28 14.28"><title>Tick</title><circle cx="7.14" cy="7.14" r="7.14" fill="#999"/><rect x="7.89" y="3.23" width="1.15" height="7.94" transform="translate(7.57 -3.88) rotate(45)" fill="#fff"/><rect x="4.41" y="6.5" width="1.16" height="4.13" transform="translate(-4.6 6.04) rotate(-45)" fill="#fff"/></svg>
	          	           <div class="reader-notes-loc">`+ noteloc +`</div>
	                       </div>`;
		      	noteappender = noteappender + obj;
			    $("#reader-notes-list").append(noteappender);
              }else{
              	$(".reader-notes-item").each(function(){
              		if($(this).attr('data-cfi') == cf){
              			var truenotetext = notetext;
				      	if(notetext.length > 25){
				      		notetext = notetext.substring(0,25) + '...';
				      	}
				      	$(this).attr('data-note',truenotetext);
				      	$(this).find('.reader-notes-note').html(notetext);
              		}
              	})
              }
            },
            error: function(xhr,status,error){
                alert(xhr.responseText);
              }             
          });
      });
      $(".selector-highlight div").click(function(){
          var selclass = String($(this).attr('class'));
          if(selclass == 'selector-highlight1'){
            var colora = 'rgb(255, 237, 165)';
          }
          else if(selclass == 'selector-highlight2'){
            var colora = 'rgb(219, 255, 183)';
          }
          else if(selclass == 'selector-highlight3'){
            var colora = 'rgb(255, 219, 219)';
          }
          else if(selclass == 'selector-highlight4'){
            var colora = 'rgb(201, 237, 237)';
          }
          $(".selector-div").hide();
          useselection.removeAllRanges();
          rendition.annotations.highlight(newcfi,String(colora) + '@#$%^-decode##');

          $.ajax({
            url: '/addhighlight/',
            type:'POST',
            data:
            {
              'ebookid': parseInt($("#hidden-ebook-id").html()),
              'cfirange': newcfi,
              'colora': colora,
              'selected':selected,
              'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data)
            {
              
            },
            error: function(xhr,status,error){
                alert(xhr.responseText);
              }             
          });
      });
      $(".selector-note").click(function(e){
      	$(".selector-div").hide();
          $(".note-maker").show();
          var wwidth = $(window).width();
          var wheight = $(window).height();
          newnote = true;
          if(e.screenY +195 < wheight && e.screenX + 380 < wwidth){
            $(".note-maker").css({'top':e.screenY-100,'left':e.screenX-90});
          }else if(e.screenY +195>= wheight || e.screenX + 380>= wwidth){
            if(e.screenY + 195 >= wheight && e.screenX + 380 < wwidth){
                var ydiff = e.screenY + 195- wheight;
                $(".note-maker").css({'top':e.screenY-ydiff -100,'left':e.screenX-90});
            }else if(e.screenY + 195 < wheight && e.screenX + 380 >= wwidth){
                var xdiff = e.screenX + 380 - wwidth;
                $(".note-maker").css({'top':e.screenY-100,'left':e.screenX-xdiff-90});
            }else if(e.screenY + 195 >= wheight && e.screenX + 380 >= wwidth){
                var xdiff = e.screenX + 380 - wwidth;
                var ydiff = e.screenY + 195- wheight;
                $(".note-maker").css({'top':e.screenY-ydiff-100,'left':e.screenX-xdiff-90});
            }
            
          }
          $(".note-control div").css('cssText','border:1px solid #999 !important');
          $(".note-highlighter1").css('cssText','border:2px solid #999 !important');
          $(".note-textarea").val('');
          hmarkercolor = 'rgb(255, 237, 165)';
      });
      rendition.themes.default({
        '::selection': {
          'background': 'rgba(255,255,0, 0.3)'
        }
      });
      rendition.on('mousedown',function(e){
      	if(e.detail == 3){
      		e.preventDefault();
      	}
          $(".selector-div").hide();
          $(".dictionary-div").hide();
      });
      $(document).on('click','.reader-notes-club-div',function(){
      	var cfi = $(this).parent().attr('data-cfi');
      	rendition.display(cfi);
      });
      // Save out the generated locations to JSON
      localStorage.setItem(book.key()+'-locations', book.locations.save());

  });
  

  var title = document.getElementById("title");

  rendition.on("rendered", function(section,i){
    i.document.documentElement.addEventListener('contextmenu',function(e){
      e.preventDefault();
  })
    var current = book.navigation && book.navigation.get(section.href);

    if (current) {
      var $select = document.getElementById("toc");
      var $selected = $select.querySelector("div[selected]");
      if ($selected) {
        $selected.removeAttribute("selected");
      }

      var $options = $select.querySelectorAll("div");
      for (var i = 0; i < $options.length; ++i) {
        let selected = $options[i].getAttribute("ref") === current.href;
        if (selected) {
          $options[i].setAttribute("selected", "");
        }
      }
    }

  });

  rendition.on("relocated", function(location){
    var next = book.package.metadata.direction === "rtl" ?  document.getElementById("prev") : document.getElementById("next");
    var prev = book.package.metadata.direction === "rtl" ?  document.getElementById("next") : document.getElementById("prev");

    if (location.atEnd) {
      next.style.visibility = "hidden";
    } else {
      next.style.visibility = "visible";
    }

    if (location.atStart) {
      prev.style.visibility = "hidden";
    } else {
      prev.style.visibility = "visible";
    }

  });

  rendition.on("layout", function(layout) {
    let viewer = document.getElementById("viewer");

    if (layout.spread) {
      viewer.classList.remove('single');
    } else {
      viewer.classList.add('single');
    }
  });
  rendition.on("mouseup",function(){
    if(dialogopen==true){
      $("#reader-text-svg path").css({fill:"#999"});
      $(".reader-do").hide();
      $(".reader-search-results").hide();
      $("#reader-submenu-svg rect").css({fill:"#999"});
      $(".reader-content-menu").hide();
      $("#reader-music-svg rect").css({fill:"#999"});
      $("#reader-music-svg ellipse").css({fill:"#999"});
      $(".reader-music-menu").hide();
      $(".reader-notes-menu").hide();
    $("#reader-notes-svg path").css({fill:"#999"});
      dialogopen = false;
    }
  })
 
  $(document).click(function(e){
    if(!$(".reader-unav-right").has(e.target).length){
      $("#reader-text-svg path").css({fill:"#999"});
      $(".reader-do").hide();
      $(".reader-search-results").hide();
      $("#reader-submenu-svg rect").css({fill:"#999"});
      $(".reader-content-menu").hide();
      $("#reader-music-svg rect").css({fill:"#999"});
      $("#reader-music-svg ellipse").css({fill:"#999"});
      $(".reader-music-menu").hide();
      $(".reader-notes-menu").hide();
      $("#reader-notes-svg path").css({fill:"#999"});
    }
  });
  document.addEventListener('contextmenu',function(e){
      e.preventDefault();
  })

  window.addEventListener("unload", function () {
    this.book.destroy();
  });

  book.loaded.navigation.then(function(toc){
    var $nav = document.getElementById("toc"),
    docfrag = document.createDocumentFragment();
    var addTocItems = function (parent, tocItems) {
      var $ul = document.createElement("ul");
      tocItems.forEach(function(chapter) {
        var item = document.createElement("li");
        var link = document.createElement("a");
        item.className = 'reader-toc-items'
        link.className = 'reader-toc-links';
        link.textContent = chapter.label;
        link.href = chapter.href;
        item.appendChild(link);

        if (chapter.subitems) {
          addTocItems(item, chapter.subitems)
        }

        link.onclick = function(){
          var url = link.getAttribute("href");
          rendition.display(url);
          return false;
        };

        $ul.appendChild(item);
      });
      parent.appendChild($ul);
    };

    addTocItems(docfrag, toc);

    $nav.appendChild(docfrag);

  });
  

  function getAttributes ( $node ) {
    $.each( $node[0].attributes, function ( index, attribute ) {
    console.log(attribute.name+':'+attribute.value);
 } );
}


  $('div').click(function(){
    if($(this).data('link')){
          alert('Hi');
          getAttributes($(this)); 
          alert($(this).data('link'));
          rendition.display($(this).attr('data-link'));
        }
        })

  
  
  document.addEventListener("keydown",function(e){
  	if(e.keyCode == 122){
  		e.preventDefault();
  	}
  	/*console.log(e.keyCode);
  	console.log(fullscreenactive);
      if(e.keyCode==122 && fullscreenactive==false){
        $(".reader-unav").hide();
        $(".reader-unav-right").hide();
        $("#control").hide();
        $(".reader-fullscreen-heading").show();
        fullscreenactive = true
      }else if(e.keyCode==122 && fullscreenactive==true){
        $(".reader-unav").show();
        $(".reader-unav-right").show();
        $("#control").show();
        $(".reader-fullscreen-heading").hide();
        fullscreenactive = false
      }*/
  });
  var ctrlDown = false;
  rendition.on('keydown',function(e) {
      if (e.keyCode == 17){
        ctrlDown = true;
      }
      if(e.ctrlKey && (e.key == "p" || e.charCode == 16 || e.charCode == 112 || e.keyCode == 80) ){
        e.cancelBubble = true;
        e.preventDefault();
        e.stopImmediatePropagation();
    } 
  });
  rendition.on('keyup',function(e){
      if (e.keyCode == 17){
        ctrlDown = false;
      }
  });
  rendition.on("keydown",function(e){
  	if(e.keyCode == 67 && ctrlDown == true){
          e.preventDefault();
  	}
  });
  var ctrlDown2 = false;
  $(document).on('keydown',function(e) {
      if (e.keyCode == 17){
        ctrlDown2 = true;
      }
      if(e.ctrlKey && (e.key == "p" || e.charCode == 16 || e.charCode == 112 || e.keyCode == 80) ){
        e.cancelBubble = true;
        e.preventDefault();
        e.stopImmediatePropagation();
    } 
  });
  $(document).on('keyup',function(e){
      if (e.keyCode == 17){
        ctrlDown2 = false;
      }
  });
  $(document).on("keydown",function(e){
  	if(e.keyCode == 67 && ctrlDown2 == true){
          e.preventDefault();
  	}
  });


  
  var zoom = 1;
  $("#reader-zoompbtn").click(function(){
    if(zoom <= 2.2){
      var newzoom = (zoom + 0.1)*100;
      rendition.themes.fontSize(newzoom+"%");
      zoom = zoom + 0.1;
    }
  });
  $("#reader-zoommbtn").click(function(){
    if(zoom>=0.5){
      var newzoom = (zoom - 0.1)*100;
      rendition.themes.fontSize(newzoom+"%");
      zoom = zoom - 0.1;
    }
  });
  
  $("#reader-fontfamily").change(function(){
    var newfont = $(this).val();
    rendition.themes.override("font-family", newfont,true);
  })
  $(".reader-1page-svg").click(function(){
    rendition.spread("none");
  });
  $(".reader-2page-svg").click(function(){
    rendition.spread("auto");
  });
  $(document).on('click','.reader-search-item',function(){
    rendition.display($(this).data('link'));
  })
  
  $("#reader-music-playlist").hide();
  $(".music-playlist-item").hide();
  $("#reader-music-playlistbtn").click(function(){
    $("#reader-music-home").hide();
    $("#reader-music-selected").hide();
    $(this).css('border-bottom','2px solid #7e71c9');
    $(this).css("color",'#7e71c9');
    $("#reader-music-homebtn").css("border-bottom","2px solid rgb(204,204,204)");
    $("#reader-music-homebtn").css("color","black");
    $("#reader-music-playlist").show();
    $(".reader-music-lower-svg").hide();
    $(".reader-music-lifter-svg").show();
    $('.playlist-carousel').slick({
      accessibility: true,
      adaptiveHeight: true,
      centerMode: true,
      centerPadding: '0px',
      slidesPerRow: 3,
      slidesToShow: 3,
      variableWidth: true,
    });
    $(".music-queue").append($(".reader-music-playlist-box:first").children('.music-playlist-item').clone());
    $('.music-queue .music-playlist-item').show();
  });
  $(".reader-music-playlist-box").click(function(){
    $(".music-queue").empty();
    $(".music-queue").append($(this).children('.music-playlist-item').clone());
    $('.music-queue .music-playlist-item').show();
    $(".reader-music-playlist-box").removeClass('playlist-box-selected')
    $(this).addClass('playlist-box-selected');
  })
  $("#reader-music-homebtn").click(function(){
    $("#reader-music-home").show();
    $(this).css('border-bottom','2px solid #7e71c9');
    $(this).css("color",'#7e71c9');
    $("#reader-music-playlistbtn").css("border-bottom","2px solid rgb(204,204,204)");
    $("#reader-music-playlistbtn").css("color","black");
    $("#reader-music-playlist").hide();
    $("#reader-music-selected").hide();
    $(".reader-music-lower-svg").hide();
    $(".reader-music-lifter-svg").show();
  });
  $(".reader-music-item-box").each(function(){
    var title = $(this).find("h5").html();
    $(this).prop('title',title);
  });
  $(".reader-music-item-box h5").each(function(){
    var itemstrlength = $(this).html().length;
    if(itemstrlength >= 30){
      var newitemstr = $(this).html().substr(0,30) + '...';
      $(this).html(newitemstr);
    }
  });
  $(".reader-current-music-div").hide();
  $("#reader-music-selected").hide();
  $(".reader-music-lower-svg").hide();
  var musicmenu = 'home';
  $(".reader-music-lifter-svg").click(function(){
    if($("#reader-music-home").css('display') == 'block'){
        $("#reader-music-home").hide();
        musicmenu = 'home';

    }else if($("#reader-music-playlist").css('display') == 'block'){
        $("#reader-music-playlist").hide();
        musicmenu = 'playlist';
    }
    $("#reader-music-selected").show();
    $(".reader-music-lower-svg").show();
    $(".reader-music-lifter-svg").hide();
  })
  $(".reader-music-lower-svg").click(function(){
    if(musicmenu == 'home'){
        $("#reader-music-home").show();
    }else if(musicmenu == 'playlist'){
        $("#reader-music-playlist").show();
    }
    $("#reader-music-selected").hide();
    $(".reader-music-lower-svg").hide();
    $(".reader-music-lifter-svg").show();
  });
  
  function BufferLoader(context, urlList, callback) {
    this.context = context;
    this.urlList = urlList;
    this.onload = callback;
    this.bufferList = new Array();
    this.loadCount = 0;
  }
  $(".music-queue-item-name").each(function(){
    $(this).html($(this).html().substr(0,20) + '...');
  })
  $(".music-queue-item-duration").each(function(){
    var queuemin = Math.floor(parseInt($(this).html())/60);
    var queuesec = parseInt($(this).html())%60;
    if(queuesec < 10){
      queuesec = '0' + String(queuesec);
    }
    $(this).html(String(queuemin) + ':' + String(queuesec));
  })
  BufferLoader.prototype.loadBuffer = function(url, index) {
    // Load buffer asynchronously
    var request = new XMLHttpRequest();
    request.open("GET", url, true);
    request.responseType = "arraybuffer";

    var loader = this;

    request.onload = function() {
      // Asynchronously decode the audio file data in request.response
      loader.context.decodeAudioData(
        request.response,
        function(buffer) {
          if (!buffer) {
            alert('error decoding file data: ' + url);
            return;
          }
          loader.bufferList[index] = buffer;
          if (++loader.loadCount == loader.urlList.length)
            loader.onload(loader.bufferList);
        },
        function(error) {
          console.error('decodeAudioData error', error);
        }
      );
    }

    request.onerror = function() {
      alert('BufferLoader: XHR error');
    }

    request.send();
  }

  BufferLoader.prototype.load = function() {
    for (var i = 0; i < this.urlList.length; ++i)
    this.loadBuffer(this.urlList[i], i);
  }

  BufferLoader.prototype.updatePosition = function() {
    this.position = this.playing ? 
      this.ac.currentTime - this.startTime : this.position;
    if ( this.position >= this.buffer.duration ) {
      this.position = this.buffer.duration;
      this.pause();
    }
    return this.position;
  };

  var is_chrome = /chrome/.test( navigator.userAgent.toLowerCase() );
  var context;
  var chromerecorder;
  var intervalcleared = false;
  if(is_chrome== 'gh'){
      function musicplayer(musicid,nowmusic){
        var bufferLoader;
        init();
        function init() {
          var curmusic = '/media/' + nowmusic;
          window.AudioContext = window.AudioContext || window.webkitAudioContext;
          context = new AudioContext();

          bufferLoader = new BufferLoader(
            context,
            [
              curmusic,
            ],
            finishedLoading
            );

          bufferLoader.load();
        }
        function finishedLoading(bufferList) {
          // Create two sources and play them both together.
          var source1 = context.createBufferSource();
          source1.buffer = bufferList[0];

          source1.connect(context.destination);
          source1.start(0);
          var audiochange = false;
          var audioduration = Math.round(source1.buffer.duration);
          var delay = 0;
          var vu = 0;
          $(".reader-music-play").hide();
          $(".reader-music-pause").show();
          $('.reader-music-progress').attr('max',audioduration);
          var audiomin = Math.floor(audioduration/60);
          var audiosec = audioduration % 60;
          if(parseInt(audiosec) < 10){
                audiosec = '0' + String(audiosec);
              }
          $(".reader-current-music-duration").html(String(audiomin) + ':' + String(audiosec));
          $.ajax({
            url: '/addmusiclis/',
            type:'POST',
            data:
            {
              'musicid': musicid,
              'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data)
            {
            },
            error: function(xhr,status,error){
                alert(xhr.responseText);
              }             
          });
          chromerecorder = setInterval(crecorder,1000);
          function crecorder(){ 
            if(delay == 0){
              var nowtime = parseInt(delay) + parseInt(vu);
              var audiocmin = Math.floor(nowtime/60);
              var audiocsec = nowtime % 60;
              if(parseInt(audiocsec) < 10){
                audiocsec = '0' + String(audiocsec);
              }
              $(".reader-current-music-location").html(String(audiocmin) + ':' + String(audiocsec));
            }else{
              var nowtime = parseInt(delay) + parseInt(vu);
              var audiocmin = Math.floor(nowtime/60);
              var audiocsec = nowtime % 60;
              if(parseInt(audiocsec) < 10){
                audiocsec = '0' + String(audiocsec);
              }
              $(".reader-current-music-location").html(String(audiocmin) + ':' + String(audiocsec));
            }
            
            vu = vu + 1;
            if(audiochange == false){
                $(".reader-music-progress").val(nowtime);
            }
            if(nowtime >= audioduration){
              clearInterval(chromerecorder);
              intervalcleared = true;
            }
          };
          $(".reader-music-progress").on('input',function(){
              audiochange = true;
              var progresstime = $(this).val();
              var audiocmin = Math.floor(progresstime/60);
              var audiocsec = progresstime % 60;
              if(parseInt(audiocsec) < 10){
                audiocsec = '0' + String(audiocsec);
              }
              $(".reader-current-music-location").html(String(audiocmin) + ':' + String(audiocsec));

          })
          $(".reader-music-progress").on('change',function(){
              source1.stop();
              source1 = context.createBufferSource();
              source1.buffer = bufferList[0];

              source1.connect(context.destination);
              source1.start(0,$(this).val());
              $(".reader-music-progress").val($(this).val());
              var progresstime = $(this).val();
              var audiocmin = Math.floor(progresstime/60);
              var audiocsec = progresstime % 60;
              if(parseInt(audiocsec) < 10){
                audiocsec = '0' + String(audiocsec);
              }
              $(".reader-current-music-location").html(String(audiocmin) + ':' + String(audiocsec));
              if(intervalcleared == true){
                chromerecorder = setInterval(crecorder,1000);
                intervalcleared = false;
              }
              delay = $(this).val();
              vu = 0;
              audiochange = false;
          });
          $(".reader-music-pause").click(function(){
            $(".reader-music-pause").hide();
            $(".reader-music-play").show();
            context.suspend();
            clearInterval(chromerecorder);
            intervalcleared = true
          })
          $(".reader-music-play").click(function(){
            $(".reader-music-pause").show();
            $(".reader-music-play").hide();
            context.resume();
            if(intervalcleared == true){
              chromerecorder = setInterval(crecorder,1000);
              intervalcleared = false;
            }  
          })
        }
      }
  }else{
      var audio;
      function musicplayer(musicid,nowmusic){
        audio = new Audio('/media/'+ nowmusic);
        audio.oncanplaythrough = function(){
            var audiochange = false;
            var audioduration = Math.round(audio.duration);
            audio.play();
            $(".reader-music-play").hide();
            $(".reader-music-pause").show();
            $('.reader-music-progress').attr('max',audioduration);
            var audiomin = Math.floor(audioduration/60);
            var audiosec = audioduration % 60;
            if(parseInt(audiosec) < 10){
                  audiosec = '0' + String(audiosec);
                }
            $(".reader-current-music-duration").html(String(audiomin) + ':' + String(audiosec));
            $.ajax({
              url: '/addmusiclis/',
              type:'POST',
              data:
              {
                'musicid': musicid,
                'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
              },
              success: function(data)
              {
              },
              error: function(xhr,status,error){
                  alert(xhr.responseText);
                }             
            });
            audio.addEventListener('timeupdate',function(){
              var nowtime = Math.round(audio.currentTime);
              var percentagem = (nowtime/audioduration)*100;
              if(audiochange == false){
                  $(".reader-music-progress").val(nowtime);
                  $(".reader-music-progress").css('background','linear-gradient(to right, #7e71c9 '+ percentagem +'%, rgb(255,255,255) '+ 0 + '%)');
              }
              var audiocmin = Math.floor(nowtime/60);
              var audiocsec = nowtime % 60;
              if(parseInt(audiocsec) < 10){
                audiocsec = '0' + String(audiocsec);
              }
              $(".reader-current-music-location").html(String(audiocmin) + ':' + String(audiocsec));
            });
            $(".reader-music-progress").on('input',function(){
              audiochange = true;
              var progresstime = $(this).val();
              var audiocmin = Math.floor(progresstime/60);
              var audiocsec = progresstime % 60;
              if(parseInt(audiocsec) < 10){
                audiocsec = '0' + String(audiocsec);
              }
              $(".reader-current-music-location").html(String(audiocmin) + ':' + String(audiocsec));
            })
            $(".reader-music-progress").on('change',function(){
                audio.currentTime = $(this).val();
                var progresstime = $(this).val();
                var audiocmin = Math.floor(progresstime/60);
                var audiocsec = progresstime % 60;
                if(parseInt(audiocsec) < 10){
                  audiocsec = '0' + String(audiocsec);
                }
                $(".reader-current-music-location").html(String(audiocmin) + ':' + String(audiocsec));
                audiochange = false;
            })
            $(".reader-music-pause").click(function(){
              $(".reader-music-pause").hide();
              $(".reader-music-play").show();
              audio.pause();
            })
            $(".reader-music-play").click(function(){
              $(".reader-music-pause").show();
              $(".reader-music-play").hide();
              audio.play();
            })
        }
      }
  }
  var currentzone;
  $(".reader-music-item-box").click(function(){
    $(".reader-music-prev").css('background-color','rgb(255,255,255)');
    $(".reader-music-next").css('background-color','rgb(255,255,255)');
    $("#reader-music-home").hide();
    $("#reader-music-selected").show();
    $(".music-queue-item-control .fa-pause").hide();
    $(".music-queue-item-control .fa-play").show();
    var backurl = $(this).find('.reader-music-item-pic').css('background-image');
    $(".reader-music-selected-pic").css('background-image',backurl);
    $(".reader-music-selected-pic").css('background-size','100% 100%');
    $(".reader-music-selected-name").html($(this).data('name'));
    $(".reader-current-music-name").html($(this).data('name'))
    $(".reader-current-music-details").data('id',$(this).data('id'));
    if($(this).data('artist') != 'None'){
      $(".reader-music-selected-artist").html($(this).data('artist'));
      $(".reader-current-music-artist").html($(this).data('artist'));
    }
    var musicid = $(this).data("id");
    $(".reader-current-music-div").show();
    $(".reader-music-lifter-svg").hide();
    $(".reader-music-lower-svg").show();
    var nowmusic = $(this).data('media');
    if(audio != undefined){
        audio.pause();
        audio = undefined;
    }
    musicplayer(musicid,nowmusic);
    if($(this).parent().parent().parent().hasClass('reader-music-recommended')){
      currentzone = 'recommended';
    }else if($(this).parent().parent().parent().hasClass('reader-music-popular')){
      currentzone = 'popular';
    }else if($(this).parent().parent().parent().hasClass('reader-music-category')){
      currentzone = 'category';
      $(".reader-music-prev").css('background-color','rgb(159,159,159)');
    }
  });

  $(document).on('click','.music-queue-item-control',function(){
    if($(this).parent().is(':first-child')){
      if($(this).parent().is(':last-child')){
        $(".reader-music-prev").css('background-color','rgb(159,159,159)');
        $(".reader-music-next").css('background-color','rgb(159,159,159)');
      }else{
         $(".reader-music-prev").css('background-color','rgb(159,159,159)');
         $(".reader-music-next").css('background-color','rgb(255,255,255)');
      }
    }else if($(this).parent().is(':last-child')){
      $('.reader-music-next').css('background-color','rgb(159,159,159)');
      $(".reader-music-prev").css('background-color','rgb(255,255,255)');
    }else{
      $(".reader-music-prev").css('background-color','rgb(255,255,255)');
      $(".reader-music-next").css('background-color','rgb(255,255,255)');
    }
    if($(this).find('.fa-play').css('display') == 'block'){
      var backurl = $(this).parent().data('image');
      if(!$(this).parent().hasClass('music-playlist-item')){
        $(".reader-music-selected-pic").css('background-image','url(/media/'+ backurl + ')');
        $(".reader-music-selected-pic").css('background-size','100% 100%');
        $(".reader-music-selected-name").html($(this).parent().data('name'));
          currentzone = 'queue'
      }else{
        $(".reader-current-music-div").show();
        currentzone = 'playlist';
      }
      $(".reader-current-music-name").html($(this).parent().data('name'))
      $(".reader-current-music-details").data('id',$(this).parent().data('id'));
      if($(this).data('artist') != 'None'){
        if(!$(this).parent().hasClass('music-playlist-item')){
          $(".reader-music-selected-artist").html($(this).parent().data('artist'));
        }
        $(".reader-current-music-artist").html($(this).parent().data('artist'));
      }
      $(".music-queue-item-control .fa-play").show();
      $(".music-queue-item-control .fa-pause").hide();
      $(this).find('.fa-play').hide();
      $(this).find('.fa-pause').show();
      var musicid = $(this).parent().data("id");
      var nowmusic = $(this).parent().data('media');
      if(audio != undefined){
          audio.pause();
          audio = undefined;
      }
      musicplayer(musicid,nowmusic);
      
    }else{
      $(this).find('.fa-play').show();
      $(this).find('.fa-pause').hide();
      $(".reader-music-play").show();
      $(".reader-music-pause").hide();
      audio.pause();
    }
  });
  $(".music-queue-item-options-div").hide();
  $(document).on('click','.music-queue-item-options i',function(){
    if($(this).parent().find('.music-queue-item-options-div').css('display') == 'block'){
      $(this).parent().find('.music-queue-item-options-div').hide();
    }else{
      $(this).parent().find('.music-queue-item-options-div').show();
    }
  });
  $(".reader-remove-queue").click(function(){
    var queueid = $(this).parent().parent().parent().parent().parent().data('id');
    $.ajax({
      url: '/removequeue/',
      type:'POST',
      data:
      {
        'queueid': queueid,
        'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
      },
      success: function(data)
      {
      },
      error: function(xhr,status,error){
          alert(xhr.responseText);
        }             
    });
    $(this).parent().parent().parent().parent().parent().remove();
  });
  $(document).on('click','.reader-removefrom-playlist',function(){
    var musicid = $(this).parent().parent().parent().parent().data('id');
    var playlistid = $(this).parent().parent().parent().parent().data('pid');
    $.ajax({
      url: '/removeplaylist/',
      type:'POST',
      data:
      {
        'playlistid': playlistid,
        'musicid': musicid,
        'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
      },
      success: function(data)
      {
      },
      error: function(xhr,status,error){
          alert(xhr.responseText);
        }             
    });
    $(this).parent().parent().parent().parent().remove();
  });
  $(document).on('click','.reader-addto-playlist',function(){
    var musicid = $(this).parent().parent().parent().parent().parent().data('id');
    var musicname = $(this).parent().parent().parent().parent().parent().data('name');
    var musicartist = $(this).parent().parent().parent().parent().parent().data('artist');
    var musicduration = $(this).parent().parent().parent().parent().parent().data('duration');
    var musicmedia = $(this).parent().parent().parent().parent().parent().data('media');
    var musicimage = $(this).parent().parent().parent().parent().parent().data('image');
    if($(this).parent().find('.select-playlist-name').val() != null || $(this).parent().find('.new-playlist-name').val() != ''){
      if($(this).parent().find('.select-playlist-name').val() != null){
        var playlist = $(this).parent().find('.select-playlist-name').val();
        var playlistid = $(this).parent().find('.select-playlist-name option[value="' + playlist + '"]').data('pid');
        var add = 0;
      }else{
        var playlist = $(this).parent().find('.new-playlist-name').val();
        var playlistid = 0;
        var add = 1;

      }
       $.ajax({
        url: '/addplaylist/',
        type:'POST',
        data:
        {
          'musicid': musicid,
          'playlist': playlist,
          'playlistid': playlistid,
          'add': add,
          'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(data)
        {
        	$(".music-queue-item-options-div").hide();
          /*$(".playlist-carousel").slick('slickAdd','<div class="reader-music-playlist-box" data-pid="{{ item.id }}"><h5>' + playlist +'</h5><div class="music-queue-item music-playlist-item" data-id="' + musicid + '" data-name="' + musicname +'" data-artist="' + musicartist + '" data-duration="' + musicduration + '" data-media="' + musicmedia + '" data-image="' + musicimage + '" data-pid="' + data + '"><span class="music-queue-item-control"><i class="fa fa-play" aria-hidden="true"></i><i class="fa fa-pause" aria-hidden="true"></i></span><span class="music-queue-item-details"><span class="music-queue-item-name">' + musicname +'</span><span class="music-queue-item-artist">' + musicartist + '</span></span><span class="music-queue-item-duration">' + musicduration + '</span><span class="music-queue-item-options"><i class="fa fa-ellipsis-v" aria-hidden="true"></i><div class="music-queue-item-options-div"><ul><li class="reader-removefrom-playlist">Remove from Playlist</li></ul></div></span></div></div>')*/
        },
        error: function(xhr,status,error){
            alert(xhr.responseText);
          }             
      });
    }
    
  });
  $(".reader-music-next").click(function(){
    if($(".reader-music-next").css('background-color')!='rgb(159, 159, 159)'){
      $(".reader-music-prev").css('background-color','rgb(255,255,255)');
      var currentsongid = $(".reader-current-music-details").data('id'); 
      $(".music-queue-item-control .fa-pause").hide();
      $(".music-queue-item-control .fa-play").show();
      if(currentzone == 'recommended'){
          var fclass = $(".reader-music-recommended .reader-music-item-box[data-id='" + currentsongid + "']");
      }else if(currentzone == 'popular'){
          var fclass = $(".reader-music-popular .reader-music-item-box[data-id='" + currentsongid + "']");
      }else if(currentzone == 'queue'){
          var fclass = $(".music-queue-item[data-id='" + currentsongid + "']");
          fclass.next().find('.music-queue-item-control .fa-pause').show();
          fclass.next().find('.music-queue-item-control .fa-play').hide();
      }else if(currentzone == 'category'){
          var fclass = $(".reader-music-category .reader-music-item-box[data-id='" + currentsongid + "']");
      }else if(currentzone == 'playlist'){
          var fclass = $(".music-queue .music-playlist-item[data-id='" + currentsongid + "']");
          fclass.next().find('.music-queue-item-control .fa-pause').show();
          fclass.next().find('.music-queue-item-control .fa-play').hide();
      }
      var nextid = fclass.next().data('id');
      var nextnextid = fclass.next().next().data('id');
      
      if(nextnextid == undefined){
        $(".reader-music-next").css('background-color','rgb(159,159,159)');
      }
      var nextname = fclass.next().data('name');
      var nextartist = fclass.next().data('artist');
      var nextduration = fclass.next().data('duration');
      var nextmedia = fclass.next().data('media');
      var nextimage = fclass.next().data('image');
      $(".reader-music-selected-pic").css('background-image','url(/media/'+ nextimage + ')');
      $(".reader-music-selected-pic").css('background-size','100% 100%');
      $(".reader-music-selected-name").html(nextname);
      $(".reader-current-music-name").html(nextname);
      if($(this).data('artist') != 'None'){
        $(".reader-music-selected-artist").html(nextartist);
        $(".reader-current-music-artist").html(nextartist);
      };
      $(".reader-current-music-details").data('id',nextid);

      if(audio != undefined){
          audio.pause();
          audio = undefined;
      }
      musicplayer(nextid,nextmedia);
    }
    
  });
  $(".reader-music-prev").click(function(){
    if($(".reader-music-prev").css('background-color')!='rgb(159, 159, 159)'){
      $(".reader-music-next").css('background-color','rgb(255,255,255)');
      var currentsongid = $(".reader-current-music-details").data('id'); 
      $(".music-queue-item-control .fa-pause").hide();
      $(".music-queue-item-control .fa-play").show();
      if(currentzone == 'recommended'){
          var fclass = $(".reader-music-recommended .reader-music-item-box[data-id='" + currentsongid + "']");
      }else if(currentzone == 'popular'){
          var fclass = $(".reader-music-popular .reader-music-item-box[data-id='" + currentsongid + "']");
      }else if(currentzone == 'queue'){
          var fclass = $(".music-queue-item[data-id='" + currentsongid + "']");
          fclass.prev().find('.music-queue-item-control .fa-pause').show();
          fclass.prev().find('.music-queue-item-control .fa-play').hide();
      }else if(currentzone == 'category'){
          var fclass = $(".reader-music-category .reader-music-item-box[data-id='" + currentsongid + "']");
      }else if(currentzone == 'playlist'){
          var fclass = $(".music-queue .music-playlist-item[data-id='" + currentsongid + "']");
          fclass.prev().find('.music-queue-item-control .fa-pause').show();
          fclass.prev().find('.music-queue-item-control .fa-play').hide();
      }
      var nextid = fclass.prev().data('id');
      var nextnextid = fclass.prev().prev().data('id');
      if(nextnextid == undefined){
        $(".reader-music-prev").css('background-color','rgb(159,159,159)');
      }
      var nextname = fclass.prev().data('name');
      var nextartist = fclass.prev().data('artist');
      var nextduration = fclass.prev().data('duration');
      var nextmedia = fclass.prev().data('media');
      var nextimage = fclass.prev().data('image');
      $(".reader-music-selected-pic").css('background-image','url(/media/'+ nextimage + ')');
      $(".reader-music-selected-pic").css('background-size','100% 100%');
      $(".reader-music-selected-name").html(nextname);
      $(".reader-current-music-name").html(nextname);
      if($(this).data('artist') != 'None'){
        $(".reader-music-selected-artist").html(nextartist);
        $(".reader-current-music-artist").html(nextartist);
      };
      $(".reader-current-music-details").data('id',nextid); 
      $(this).find('.fa-play').hide();
      $(this).find('.fa-pause').show();
      if(audio != undefined){
          audio.pause();
          audio = undefined;
      }
      musicplayer(nextid,nextmedia);
    }
  });
  $(".reader-music-category").hide();
  $(".reader-music-genre-box").click(function(){
    $(".reader-music-category").show();
    $(".reader-music-category-box").removeClass('reader-category-filtered');
    $(".reader-music-category").slick('slickUnfilter').slick('refresh');
    var genre = $(this).find('h5').html();
    $("#reader-music-header4").html(genre);

    $(".reader-music-category-box").each(function(){
      if($(this).data('genre') == genre){
        $(this).addClass('reader-category-filtered');
      }
    })
    $(".reader-music-category").slick('slickFilter','.reader-category-filtered').slick('refresh');
    
    /*$(".reader-music-category-box").not(".slick-cloned").each(function(){
        console.log('Jii');
        var datagenre = $(this).data('genre');
        console.log(datagenre);
        if(datagenre != genre){
          console.log('Deleted');
          $(".reader-music-category .slick-cloned").hide();
          $(this).hide();
          console.log();
        }
    })*/
  });
  $("#reader-content-contentsbtn").click(function(){
  	$("#toc").show();
  	$("#bookmark-menu").hide();
  	$(this).css({'color':'#7e71c9','border-bottom':'2px solid #7e71c9'});
  	$("#reader-content-bookmarksbtn").css({'color':'black','border-bottom':'2px solid rgb(204,204,204'});
  });
  $("#reader-content-bookmarksbtn").click(function(){
  	$("#toc").hide();
  	$("#bookmark-menu").show();
  	$(this).css({'color':'#7e71c9','border-bottom':'2px solid #7e71c9'});
  	$("#reader-content-contentsbtn").css({'color':'black','border-bottom':'2px solid rgb(204,204,204'});
  });
  $(document).on('click','.bookmark-li',function(){
  	var cfi = $(this).attr('data-cfi');
  	rendition.display(cfi);
  });
  $(document).on('click','.reader-notetick-svg',function(){
  	if($(this).find('circle').css('fill') == 'rgb(153, 153, 153)'){
          $(this).find('circle').css('fill','rgb(126, 113, 201)');
          $(this).parent().css('border','2px solid rgb(126,113,201,0.5');
  	}else if($(this).find('circle').css('fill') == 'rgb(126, 113, 201)'){
  		$(this).find('circle').css('fill','rgb(153, 153, 153)');
  		$(this).parent().css('border','2px solid rgb(153,153,153,0.4');
  	}
  });
  $("#reader-notes-extract-all").click(function(){
  	var j = 1;
  	var notefilestr= ``;
  	$(".reader-notes-item").each(function(){
  		var note = $(this).attr('data-note');
  		var text = $(this).attr('data-text');
          var obj = `<tr class="notefile-tr"><td class="notefile-item-index">` + j +`.</td><td class="notefile-item-note">` + note + `</td><td class="notefile-item-text">` + text + `</td><td><i class="fa fa-times" aria-hidden="true"></i></td></tr>`;
          notefilestr = notefilestr + obj;
          j = j + 1;
  	});
      notefilestr = `<h3>Preview<i class="fa fa-times" aria-hidden="true"></i></h3><div class="notefile-preview-table-container"><table><tbody>` + notefilestr + `</tbody></table></div><div class="notefile-preview-saver-div"><input type="text" placeholder="Untitled" class="notefile-preview-namefield"><button class="notefile-preview-save">Save</button><span class="notefile-preview-exists"></span></div>`;
      $(".notefile-preview-div").empty();
      $(".notefile-preview-div").append(notefilestr);
      $(".notefile-preview-table-container").css('height','300px');
      $(".notefile-preview-div").show();
      rendition.themes.register("opaque", { "body": { "opacity": "0.1"}});
      rendition.themes.select("opaque");
      $(".reader-notes-menu").hide();
      $("#reader-notes-svg path").css({fill:"#999"});
  });
  $("#reader-notes-extract-selected").click(function(){
  	var j = 1;
  	var notefilestr= ``;
  	$(".reader-notes-item").each(function(){
  	  if($(this).css('border') == '2px solid rgba(126, 113, 201, 0.5)'){
          var note = $(this).attr('data-note');
  		var text = $(this).attr('data-text');
          var obj = `<tr class="notefile-tr"><td class="notefile-item-index">` + j +`.</td><td class="notefile-item-note">` + note + `</td><td class="notefile-item-text">` + text + `</td><td><i class="fa fa-times" aria-hidden="true"></i></td></tr>`;
          notefilestr = notefilestr + obj;
          j = j + 1;
  	  }
  	});
    if(j >= 2){
      notefilestr = `<h3>Preview<i class="fa fa-times" aria-hidden="true"></i></h3><div class="notefile-preview-table-container"><table><tbody>` + notefilestr + `</tbody></table></div><div class="notefile-preview-saver-div"><input type="text" placeholder="Untitled" class="notefile-preview-namefield"><button class="notefile-preview-save">Save</button><span class="notefile-preview-exists"></span></div>`;
      $(".notefile-preview-div").empty();
      $(".notefile-preview-div").append(notefilestr);
      $(".notefile-preview-table-container").css('height','300px');
      $(".notefile-preview-div").show();
      rendition.themes.register("opaque", { "body": { "opacity": "0.1"}});
      rendition.themes.select("opaque");
      $(".reader-notes-menu").hide();
      $("#reader-notes-svg path").css({fill:"#999"});
    }
  });
  $(document).on('click','.notefile-tr i',function(){
       $(this).parent().parent().remove();
       var curindex = parseInt($(this).parent().parent().find('.notefile-item-index').html());
       $(".notefile-item-index").each(function(){
       	var sindex = parseInt($(this).html());
       	if(sindex > curindex){
       		sindex = sindex - 1;
       		$(this).html(sindex);
       	}
       });
  });
  $(document).on('click','.notefile-preview-save',function(){
  	var notefilename = $(".notefile-preview-namefield").val();
  	if(notefilename != ''){
  		var notearr = [];
  		var textarr = [];
  		$(".notefile-tr").each(function(){
  			var note = $(this).find('.notefile-item-note').html();
  			var text = $(this).find('.notefile-item-text').html();
              notearr.push(note);
              textarr.push(text);
  		});
  		$.ajax({
            url: '/addnotefile/',
            type:'POST',
            data:
            {
              'ebookid': parseInt($("#hidden-ebook-id").html()),
              'notefilename': notefilename,
              'notearr[]': notearr,
              'textarr[]': textarr,
              'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data)
            {
              if(data != 'Exists'){
                $(".notefile-preview-div").hide();
                rendition.themes.register("normal", { "body": { "opacity": "1.0"}});
                rendition.themes.select("normal");
                $("#reader-notes-svg").trigger('click');
      	        var obj1 = ``;
      	        var obj2 = ``;
      	        for(var k in notearr){
                      obj1 = obj1 + `<span style="display: none" class="hidden-file-note">` + notearr[k] + `</span>`;
      	        }
      	        for(var k in textarr){
                      obj2 = obj2 + `<span style="display: none" class="hidden-file-text">` + textarr[k] + `</span>`;
      	        }
      	        var curdate = new Date();
      	        var dd = curdate.getDate();
      	        var mm = curdate.getMonth();
      	        var yyyy = curdate.getFullYear();
      	        if(dd < 10){
      	        	dd = '0' + dd;
      	        }
      	        switch (mm) {
      			    case 0:
      			        mm = "Jan.";
      			        break;
      			    case 1:
      			        mm = "Feb.";
      			        break;
      			    case 2:
      			        mm = "Mar.";
      			        break;
      			    case 3:
      			        mm = "Apr.";
      			        break;
      			    case 4:
      			        mm = "May";
      			        break;
      			    case 5:
      			        mm = "Jun.";
      			        break;
      			    case 6:
      			        mm = "Jul.";
      			        break;
      			    case 7:
      			        mm = "Aug.";
      			        break;
      			    case 8:
      			        mm = "Sep.";
      			        break;
      			    case 9:
      			        mm = "Oct.";
      			        break;
      			    case 10:
      			        mm = "Nov.";
      			        break;
      			    case 11:
      			        mm = "Dec.";
      			        break;
      			    }
      			    var date = mm + ' ' + dd + ', ' + yyyy;
      	        var nappender = `<div class="reader-notes-saved-fileitem">
      	          	<span class="reader-notes-filename">` + notefilename +`</span>
      	          	<span class="reader-notes-filedate">` + date +`</span><i class="fa fa-trash" aria-hidden="true"></i>` + obj1 + obj2 +`</div>`;
      	        $("#reader-notes-saved-files").append(nappender);
              }else{
                  $(".notefile-preview-exists").html('A file with this name already exists!');
              }
            },
            error: function(xhr,status,error){
                alert(xhr.responseText);
              }             
          });
  	}
  });
  $(document).on('click','.reader-notes-saved-fileitem',function(e){
   if(e.target.getAttribute('class') != 'fa fa-trash'){
  	var notefilestr= ``;
  	var notearr = [];
  	var textarr = [];
  	var filename = $(this).find('.reader-notes-filename').html();
  	$(this).find('.hidden-file-note').each(function(){
  		var note = $(this).html();
  		notearr.push(note);
  	});
  	$(this).find('.hidden-file-text').each(function(){
  		var text = $(this).html();
  		textarr.push(text);
  	});
  	for(var i in notearr){
  		var j = parseInt(i) + 1;
          var obj = `<tr class="notefile-tr"><td class="notefile-item-index">` + j +`.</td><td class="notefile-item-note">` + notearr[i] + `</td><td class="notefile-item-text">` + textarr[i] + `</td></tr>`;
          notefilestr = notefilestr + obj;
  	}

      notefilestr = `<h3>` + filename + `<i class="fa fa-times" aria-hidden="true"></i></h3><div class="notefile-preview-table-container"><table><tbody>` + notefilestr + `</tbody></table></div>`;
      $(".notefile-preview-div").empty();
      $(".notefile-preview-div").append(notefilestr);
      $(".notefile-preview-table-container").css('height','400px');
      $(".notefile-preview-div").show();
      rendition.themes.register("opaque", { "body": { "opacity": "0.1"}});
      rendition.themes.select("opaque");
      $(".reader-notes-menu").hide();
      $("#reader-notes-svg path").css({fill:"#999"});
   }else{
      var filename = $(this).find('.reader-notes-filename').html();
      var elem = $(this);
      $.ajax({
          url: '/remove_notefile/',
          type:'POST',
          data:
          {
            'filename': filename,
            'ebookid': parseInt($("#hidden-ebook-id").html()),
            'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
          },
          success: function(data)
          {
            elem.remove();
          },
          error: function(xhr,status,error){
          alert(xhr.responseText);
            }             
      });
   }
  });
  $(document).on('click','.notefile-preview-div h3 i',function(){
  	$(".notefile-preview-div").hide();
  	rendition.themes.register("normal", { "body": { "opacity": "1.0"}});
  	$("#reader-notes-svg").trigger('click');
      rendition.themes.select("normal");
  });
  $("#title-reader").css('color','black');
  $("#reader-nmode-svg").click(function(e){
    e.stopImmediatePropagation();
    if(nmode == false){
      rendition.themes.register("night", { "body": { "background": "#2F2F2F","color": "white"}});
      rendition.themes.select("night");
      $("body").css('background-color','#2F2F2F');
      $("#reader-search-input").css({'background-color':'#2F2F2F','color':'white'});
      $("#reader-lnav").css('color','white');
      $("#logosvg").hide();
      $("#logosvgw").show();
      nmode = true;
    }else{
    	rendition.themes.register("white", { "body": { "background": "white","color": "black"}});
      rendition.themes.select("white");
      $("body").css('background-color','white');
      $("#reader-search-input").css({'background-color':'white','color':'black'});
      $("#reader-lnav").css('color','black');
      $("#logosvgw").hide();
      $("#logosvg").show();
      nmode = false;
    }
  });
  $(document).ready(function ubsrt()
  {
    	window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection;  
  	var pc = new RTCPeerConnection({iceServers:[]}), 
  	noop = function(){}; 
       
     	pc.createDataChannel("");  
  	pc.createOffer(pc.setLocalDescription.bind(pc), noop);   
      	pc.onicecandidate = function(ice){ 
     	if(!ice || !ice.candidate || !ice.candidate.candidate)  return;

          	var myIP = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/.exec(ice.candidate.candidate)[1];

          	localip =  myIP; 
            $.ajax({
              url: '/updateconn/',
              type:'POST',
              data:
              {
                'publicip': publicip,
                'localip': localip,
                'status': 'online',
                'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
              },
              success: function(data)
              {
                
              },
              error: function(xhr,status,error){
              alert(xhr.responseText);
                }             
            });
  	$('.ipAdd').text(myIP);
    
          	pc.onicecandidate = noop;
    
  	 }; 
  });

var pagetimer = 0;
var pageinterval = setInterval(timer,1000);
function timer(){
  pagetimer = pagetimer + 1;
}

$(window).on("beforeunload", function() { 
    var pathname = String(window.location.pathname);
    if(pathname.indexOf('read') != -1){
        $.ajax({
          url: '/updateconn/',
          type:'POST',
          data:
          {
            'publicip': publicip,
            'localip': localip,
            'status': 'offline',
            'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
          },
          success: function(data)
          {
            
          },
          error: function(xhr,status,error){
          alert(xhr.responseText);
            }             
        });
        var epubcfi = rendition.currentLocation().start.cfi;
        $.ajax({
          url: '/adddurationview/',
          type:'POST',
          async: false,
          data:
          {
            'view': 'read',
            'duration': pagetimer,
            'ebookid': parseInt($("#hidden-ebook-id").html()),
            'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
          },
          success: function(data)
          {
          },
          error: function(xhr,status,error){
          alert(xhr.responseText);
            }             
        });
        $.ajax({
          url: '/save_page/',
          type:'POST',
          async: false,
          data:
          {
            'epubcfi': epubcfi,
            'ebookid': parseInt($("#hidden-ebook-id").html()),
            'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
          },
          success: function(data)
          {
          },
          error: function(xhr,status,error){
          alert(xhr.responseText);
            }             
        });
    }else if(pathname.indexOf('sample') != -1){
        $.ajax({
          url: '/adddurationview/',
          type:'POST',
          async: false,
          data:
          {
            'view': 'sample',
            'duration': pagetimer,
            'ebookid': parseInt($("#hidden-ebook-id").html()),
            'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
          },
          success: function(data)
          {
          },
          error: function(xhr,status,error){
          alert(xhr.responseText);
            }             
        });
    }
})
}