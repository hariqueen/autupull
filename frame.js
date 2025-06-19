var fnObj = {};
var frmAction = SCRIPT_PROJECT.ipccYn == "Y" ? eval("CTI_ACTIONS") : {};
var _ipccYn   = SCRIPT_PROJECT.ipccYn;
var _befCounsType = "";
var ACTIONS = axboot.actionExtend(fnObj, $.extend(frmAction,{
    PAGE_SEARCH: function (caller, act, data) {
        return false;
    },
    TOGGLE_ASIDE: function (caller, act, data) {
        caller.frameView.toggleAside();
    },
    MENU_OPEN: function (caller, act, data) {
        caller.tabView.open(data);
    },
    TOGGLE_FULLSCREEN: function (caller, act, data) {
        caller.frameView.toggleFullScreen();
    },
    LOGOUT : function(caller, act, msgFlag){
        if(!$("[data-page-btn=logout]").hasClass("disable")){
        	if(msgFlag){
    	    	axDialog.confirm({
    				msg: MSG("message.alert.confirm","label.common.logout")
    			}, function (){
    				if (this.key == "ok") {
    				    var axUseCti = ax5.util.nvl(top.ax_use_cti,false);
    				    if(axUseCti)
                        {
    				        try {
    				            if(ctiBtnChk())
                                {
                                    if(CAPI)
                                   {
										top.ACTIONS.dispatch(top.ACTIONS.CHANNEL_SAVE, "");
                                        CAPI.logout();
                                        location.href = CONTEXT_PATH + "/api/logout";
                                   }
                                   else if(CAPI == null)
                                   {
										top.ACTIONS.dispatch(top.ACTIONS.CHANNEL_SAVE, "");
                                       	location.href = CONTEXT_PATH + "/api/logout";
                                   }
                               }
    				        }catch(e){
								top.ACTIONS.dispatch(top.ACTIONS.CHANNEL_SAVE, "");
    				            try{CAPI.logout();}catch(e){};
    				            location.href = CONTEXT_PATH + "/api/logout";
    				        }
                        }else{
							top.ACTIONS.dispatch(top.ACTIONS.CHANNEL_SAVE, "");
                            location.href = CONTEXT_PATH + "/api/logout";    
                        }
    				}
    			});
        	}else{
				top.ACTIONS.dispatch(top.ACTIONS.CHANNEL_SAVE, "");
        		location.href = CONTEXT_PATH + "/api/logout";
        	}
        }
    },
    CHANGE_PROJ : function(caller, act, data){
		axboot.ajax({
			type: "POST",
			url: ["users","changeLoginProj"],
			data: JSON.stringify({loginProjCd : $("[data-ax-path=loginProjCd]").val()}),
			callback: function (res) {
				var formConfig = {url   :  "/jsp/main.jsp"
				                ,target : "_self"};
				
				ax5.util.dynamicSubmit(formConfig);
			}
		});
    },
    SAVE_MEMO : function(caller, act, initFlag){
        var memoObj = $("[data-ax-path=memo]");
        if(initFlag) memoObj.val("");
        
        var memo = memoObj.val();
        var data = {userId : SCRIPT_SESSION.userId ,memo : memo};
        axboot.ajax({
            type: "POST",
            url: ["users","updateUserMemo"],
            data: JSON.stringify(data),
            callback: function (res) {
            },
            options : {
                nomask:true
            }
        });
    },
    USER_MEMO : function(caller, act, initFlag){
        var memoObj = $("[data-ax-path=memo]");
        var memo   = memoObj.val();
        
        var data   = {userId : SCRIPT_SESSION.userId ,memo : memo};
        var params = {modalType : "USER_MEMO"
                     ,sendData  : data
                     ,callback  : function(memo){
                         $("[data-ax-path=memo]").val(memo);
                         ACTIONS.dispatch(ACTIONS.SAVE_MEMO,false);
                     }};
        
        ax5.util.openModal(params); 
    },
    SEARCH_PROJ : function(caller, act, data){
        var params  = {useYn : "Y"};
        var projObj = $("[data-ax-path=loginProjCd]");
        if(projObj.length > 0) {
            var projCd  = projObj.val();
            axboot.ajax({
                type: "POST",
                url: ["project","selectProjectList"],
                data: JSON.stringify(params),
                callback: function (res) {
                    projObj.find("option").remove();
                    var list = res.list;
                    var chkCnt = 0;
                    for(var i=0;i<list.length;i++){
                        var info = list[i];
                        if(projCd == info["projCd"]){
                            projObj.append($("<option value='"+info["projCd"]+"' selected>"+info["projNm"]+"</option>"));
                            chkCnt++;
                        }else{
                            projObj.append($("<option value='"+info["projCd"]+"'>"+info["projNm"]+"</option>"));
                        }
                    }
                    if(chkCnt == 0){
                        ACTIONS.dispatch(ACTIONS.CHANGE_PROJ);
                    }
                },
                options : {
                    nomask : true
                }
            }); 
        }
    },
    CLICK_STATUS : function(caller, act, data){
        
        var type   = data["type"];
        var target = data["target"];
        var idx    = data["idx"];
        var toastObjs = $('[data-ax5-ui=toast]');
        for(var i=0;i<toastObjs.length;i++){
            var toastObj = $(toastObjs[i]);
            var id= toastObj.prop("id");
            var idArr = id.split("-");
            if(idArr.length > 0){
            var tId = idArr[idArr.length-1];
                if(tId == idx) {
                    toastObj.remove();
                    break;
                }
            }
        }
        
        var menuList = [];
        if(type == "home") {
            if(HOME_MENU_DATA.length > 0){
                var homeMenuCd = HOME_MENU_DATA[0].menuCd;
                fnObj.tabView.click(homeMenuCd);
                var tabObj = $("iframe[data-tab-id='"+homeMenuCd+"']").get(0).contentWindow;
                tabObj.fnObj.topLeftView.searchTabList(target);
            }
        }else {
            var menuList = ax5.util.filter(TOP_MENU_DATA,function(){
                var program = target + ".jsp";
                var progArr = this.program.split("/");
                if(program == progArr[progArr.length-1]){
                    return true;
                } 
            });
            if(menuList.length > 0){
                fnObj.tabView.open(menuList[0]);
            }
        }
    },
    DASH_SEARCH : function(caller, act, data){
    	var interval = SCRIPT_SESSION.loginProjCd == "SAAS_BWI" ? 60000 : 300000; // 볼드워크가 아닌 경우 5분마다 체크
        var chkInterval = 60000;
        var intConfig = {idName : "asideDash"
            ,fn : function(data){
                var params = {projCd : SCRIPT_SESSION.loginProjCd,userCd : SCRIPT_SESSION.userId}
                
                if(SCRIPT_SESSION.loginProjCd == "SAC") {            		
            		var beginDay = Util.date(new Date(),{return:"yyyy-MM-dd"});
            		var endDay = Util.date(new Date(),{return:"yyyy-MM-dd"});

            		params["url"] = "http://211.47.160.249:9090/API/mobilecrm.jsp";
            		params["type"] = "sms_list,mms_list";
            		params["begin_day"] = beginDay;
            		params["end_day"] = endDay;
            		//params["begin_day"] = "2024-07-01";
            		//params["end_day"] = "2024-07-31";
            		params["member_phone"] = "01023644402";
                }
                
	                axboot.ajax({
	                    type: "POST",
	                    url: ["common","selectAsideDashInfo"],
	                    data: JSON.stringify(params),
	                    callback: function (res) {
	                        var map  = res.map;
     
	                        var nowInterval = map.noticeImp == 0 ? 600000 : 60000;
//	                        console.log("noticeImp:"+map.noticeImp+"\ninterval:"+interval+"\ncount:"+chkInterval+"\nnow:"+Util.date(new Date,{return:"yyyy-MM-dd hh:mm:ss"}));
	                        if(SCRIPT_SESSION.loginProjCd == "SAAS_BWI"){
		                        if(chkInterval == interval || interval != nowInterval){
			                        chkInterval = 60000;
		                        	if((SCRIPT_SESSION.loginProjCd == "SAAS_BWI" && map.noticeImp == 0) && interval != 600000){ // 중요공지가 없는 경우 10분마다 토스트팝업
		                        		interval = 600000;
		                        	}else if((SCRIPT_SESSION.loginProjCd == "SAAS_BWI" && map.noticeImp > 0) && interval != 60000){ // 중요공지가 있는 경우 1분마다 토스트팝업
		                        		interval = 60000;
		                        	}
//		                        	console.log("Toast Pop");
		                        	fnObj.frameView.asideView.setDashData(map);
		                        }else{
		                        	chkInterval = chkInterval + 60000;
		                        }
	                        }else{
//	                        	console.log("Toast Pop");
	                        	fnObj.frameView.asideView.setDashData(map);
	                        }
	                    },
	                    options : {
	                        nomask : true
	                    }
	                }); 

            }
            ,interval : interval};
        // 세션이 끊겨도 돌고 있으므로.. 그냥 쿠키가 삭제되면.. interval 을 죵료한다. 10분마다 모니터링
        var dashIntVal = ax5.util.setInterval(intConfig);
        var clearIntVal = setInterval(function(){
            var authKey = Util.getCookie(ICS_AUTH_KEY);
            if(Util.isNothing(authKey)){
                clearInterval(dashIntVal);
                clearInterval(clearIntVal);
                ACTIONS.dispatch(ACTIONS.FORCE_LOGOUT);
            }
        },60000)
    },
    USER_MEMO : function(caller, act, data){
        var params = {projCd : SCRIPT_SESSION.loginProjCd,userId : SCRIPT_SESSION.userId};
        axboot.ajax({
            type: "POST",
            url: ["users","selectUserMemo"],
            data: JSON.stringify(params),
            callback: function (res) {
                if(res.map){
                    $("[data-ax-path='memo']").val(Util.nvl(res.map.memo));
                }
            },
            options : {
                nomask : true
            }
        });
        return false
    },
    FORCE_LOGOUT : function (caller, act, data) {
        var params = {userId : SCRIPT_SESSION.userId,loginUserCd : SCRIPT_SESSION.userId};
        axboot.ajax({
            type : "POST",
            url  : ["users","forceUserLogout"],
            data : JSON.stringify(params),
            callback : function(){
                var axUseCti = ax5.util.nvl(top.ax_use_cti,false);
                if(axUseCti) {
                    try {
                        if(ctiBtnChk()){
                           if(CAPI){
                                CAPI.logout();
                           }
                       }
                    }catch(e){
                        try{CAPI.logout();}catch(e){};
                    }
                }
                location.href = CONTEXT_PATH + "/jsp/login.jsp";
            },
            options : {
                nomask : true
            }
        });
    },
// 사용채널 DB저장
    CHANNEL_SAVE: function (caller, act, data) {
        axboot.ajax({
            type: "POST",
            url: ["users","updateChannel"],
            data: JSON.stringify({projCd: SCRIPT_PROJECT.projCd, channel: data, userCd: SCRIPT_SESSION.userId}),
            callback: function (res) {
            },
            options: { 
            	nomask: true,
            	onError: function (err) {
                }
            }
        });
	},
	INIT_BOARD : function(caller, act, data){
		var contFrms = $(document).find("iframe");
		contFrms.each(function(){
			var frmSrc = $(this).attr("src");
			if(!Util.isNothing(frmSrc)) {
				if(frmSrc.indexOf("boardCouns.jsp") > -1){
					var frmCnt = $(this)[0].contentWindow;
					frmCnt.ACTIONS.dispatch(frmCnt.ACTIONS.PAGE_INIT,window);
				}
			}
		});
	},
	OPEN_MENU : function(caller, act, target){
		
		var topDoc = $(top.document);
		var mNode = {};
		var getNode = function(nodes,target){
			for(var i=0;i<nodes.length;i++){
				var node = nodes[i];
				if(node["program"].indexOf(target+".jsp") > -1){
					mNode = node;
					break;
				}
				if(node["children"].length > 0) {
					getNode(node["children"],target);
				}
			}
		}
		
		getNode(top.fnObj.menuItems,target);
		
		if(!$.isEmptyObject(mNode)){
			if(target == "boardCouns"){
				top.ACTIONS.dispatch(top.ACTIONS.MENU_OPEN, $.extend({}, mNode));
			}else if(target == "chatWinPop"){
                axboot.openWinPostPopup.open({id : mNode["menuCd"],url : mNode["program"] + "?menuCd=" + mNode["menuCd"]});
			}
		}
	},
    COUNS_TYPE_HANDLER : function(){
        var counsType = "";
        if(SCRIPT_SESSION.useCti == "Y"){
        	try{
	            top.fnCti.activityCTIView.initView();
	            top.fnCti.ctiButtonControl.initView();
        	}catch(e){}
            counsType = "CALL";
            $(top.document).find('input:radio[value="CALL"]').prop("checked",true);
        }else{
        	$(top.document).find('input:radio[value="CALL"]').prop("disabled",true);
        }
        
        if(SCRIPT_SESSION.chatYn == "Y"){
            top.fnChat.activityView.initView();
            if(ax5.util.isNothing(counsType)){
            	counsType = "CHAT";
            	$(top.document).find('input:radio[value="CHAT"]').prop("checked",true);
            }
        }else{
        	$(top.document).find('input:radio[value="CHAT"]').prop("disabled",true);
        }
        
        if(SCRIPT_SESSION.boardYn == "Y"){
        	if(ax5.util.isNothing(counsType)){
            	counsType = "BOARD";
                $(top.document).find('input:radio[value="BOARD"]').prop("checked",true);
            }
        }else{
        	$(top.document).find('input:radio[value="BOARD"]').prop("disabled",true);
        }
        
        var checkObj = $(top.document).find('input:radio[name="counsType"]');
        
        checkObj.on("click",function(){
        	
        	var obj = $(this);
        	var value = obj.val();
        	var parms = $.extend({},top.fnChat.activityView.defaultData,{callback : true});
        	_counsChgFlag = false;
        	
        	if(_befCounsType != value) {
	        	switch(value) {
	        		case "CALL":
						top.ACTIONS.dispatch(top.ACTIONS.CHANNEL_SAVE, "MENU_IN");
	        			if(SCRIPT_SESSION.chatYn == "Y"){
	        				top.fnChat.activityView.offChat(parms);
	        			}
	        			if(SCRIPT_SESSION.boardYn == "Y"){
	        				ACTIONS.dispatch(ACTIONS.INIT_BOARD);
	        			}
						top.ACTIONS.dispatch(top.ACTIONS.CTI_ETC);
	        		break;
	        		case "CHAT":
						top.ACTIONS.dispatch(top.ACTIONS.CHANNEL_SAVE, "MENU_CHAT");
	    				top.fnChat.activityView.onChat(parms)
	        			if(SCRIPT_SESSION.useCti == "Y"){
	        				top.ACTIONS.dispatch(top.ACTIONS.CTI_CHAT);
	        			}
	        			if(SCRIPT_SESSION.boardYn == "Y"){
	        				ACTIONS.dispatch(ACTIONS.INIT_BOARD);
	        			}
	        			/*if(_befCounsType == "BOARD") {
	        	        	var valIntId = setInterval(function(){
	        	        		if(_counsChgFlag){
	        	        			ACTIONS.dispatch(ACTIONS.OPEN_MENU,"chatWinPop");
	        	        			clearInterval(valIntId);
	        	        		}
	        	        	},500);
	                	}else{
	                		ACTIONS.dispatch(ACTIONS.OPEN_MENU,"chatWinPop");
	                	}*/
	        			//ACTIONS.dispatch(ACTIONS.OPEN_MENU,"chatWinPop");
	            	break;
	        		case "BOARD":
						top.ACTIONS.dispatch(top.ACTIONS.CHANNEL_SAVE, "MENU_BOARD");
	        			if(SCRIPT_SESSION.chatYn == "Y"){
	        				top.fnChat.activityView.offChat(parms)
	        			}
	        			if(SCRIPT_SESSION.useCti == "Y"){
	        				top.ACTIONS.dispatch(top.ACTIONS.CTI_BOARD);
	        			}
	        			ACTIONS.dispatch(ACTIONS.OPEN_MENU,"boardCouns");
	        		break;
	        	}
	        	
	        	/*if(_befCounsType == "BOARD") {
		        	var valIntId = setInterval(function(){
		        		if(_counsChgFlag){
		        			_befCounsType = value;
		        			clearInterval(valIntId);
		        		}
		        	},500);
	        	}else{
	        		_befCounsType = value;
	        	}*/
	        	_befCounsType = value;
        	}
        });
        $(top.document).find('input:radio[name="counsType"]:checked').click();
    },
	CTI_STAT : function(caller, act, data){
		
		var codeList = top.COMMON_CODE["MALL_ID"];		
		var tbodyObj = $("#callStatTbody");
		tbodyObj.empty();
		if(tbodyObj.length > 0) {
			trHtml = "";
			if(SCRIPT_PROJECT.ipccYn == "Y"){
				//Call
				trHtml += '<tr style="height: 29px;">';
				trHtml += '<td style="border : 1px solid #fff;text-align:center;">Call</td>';
				trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="inb_wait">0건</td>';
				trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="inb_per">0%</td>';
				trHtml += '</tr>';
			}
			if(SCRIPT_PROJECT.chatYn == "Y"){
				//Chat
				trHtml += '<tr style="height: 29px;">';
				trHtml += '<td style="border : 1px solid #fff;text-align:center;">Chat</td>';
				trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="chat_wait">0건</td>';
				trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="chat_per">0%</td>';
				trHtml += '</tr>';
			}
			if(SCRIPT_PROJECT.boardCounsYn == "Y"){
				//Board
				trHtml += '<tr style="height: 29px;">';
				trHtml += '<td style="border : 1px solid #fff;text-align:center;">게시판</td>';
				trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="board_wait">0건</td>';
				trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="board_per">0%</td>';
				trHtml += '</tr>';
			}
			tbodyObj.append($(trHtml));
		}
		
		var dataList = {};
		var _ipccIntIds = top.window._ipccIntIds;		
		
		console.info("_ipccIntIds",_ipccIntIds);
		
		if(!Util.isNothing(top.window._ipccIntIds)) clearInterval(_ipccIntIds);
		
		//운선생만.. cti 쪽 건드려도 되는데.. 공통이라 여기서 핸들링
		var callIpcc= function () {
			
			var url = "";
			if(location.protocol==='https:'){
		      	url = "https://" + SCRIPT_PROJECT.ipccUrl;
		    }else{
				url = "http://" + SCRIPT_PROJECT.ipccUrl;
		    }
			
			if(SCRIPT_SESSION["loginProjCd"] == "SAC"){
				url += "/call_logs?cmd=minidashinfo&center_id=11";
			}else if(SCRIPT_SESSION["loginProjCd"] == "SAC_DLI"){
				url += "/call_logs?cmd=minidashinfo&center_id=13";
			}else if(SCRIPT_SESSION["loginProjCd"] == "SAC_OLIT"){
				url += "/call_logs?cmd=minidashinfo&center_id=17";
			}else if(SCRIPT_SESSION["loginProjCd"] == "SAAS_DCI"){
				url += "/call_logs?cmd=minidash";
			}	
			
			try{
		        axboot.ajax({
		        	type: "POST",
			        url: ["callstat","selectMiniMon"],
			        data: JSON.stringify({projCd : SCRIPT_SESSION["loginProjCd"],url : url}),
			        callback: function(res) {
			        	res.map.chatBoard.forEach(function(n){
			        		if(n.channel == "CALL"){
			        			dataList = $.extend({},dataList, {inb_wait: n.inb_wait, inb_per: n.inb_per});
			        		}else if(n.channel == "CHAT"){
			        			dataList = $.extend({},dataList, {chat_wait: n.abandonCnt,chat_per:n.ibConnRate.toFixed(1)});
			        		}else{
			        			dataList = $.extend({},dataList, {board_wait: n.abandonCnt,board_per:n.ibConnRate.toFixed(1)});
			        		}
					        axboot.ajax({
					            type: "GET",
					            url: url,
					            callback: function (res) {
									if(res.result){
										var arr= res.data;
										if(arr.length > 0) {
											dataList = $.extend({},dataList, arr[0]);
											tbodyObj.find("td[id]").each(function(){
												var id= $(this).prop("id");
												if(id.indexOf("wait") > -1){
													if(dataList[id] > 0){
														var toastData = {};
														$(this).css({'background-color': '#87d842'});
														switch (id) {
														case "inb_wait":
															toastData = {inb_wait : dataList[id]};
															break;
														case "chat_wait":
															toastData = {chat_wait : dataList[id]};
															break;
														case "board_wait":
															toastData = {board_wait : dataList[id]};
															break;
														default:
															break;
														}
														if(SCRIPT_SESSION["loginProjCd"] == "SAC2-S"){
															fnObj.frameView.asideView.setDashData(toastData);
														}
													}else{
														$(this).css({'background-color': '#034a94'});
													}
													$(this).text(Util.nvl(dataList[id],"0") + "건");
												}else{
													$(this).text(Util.nvl(dataList[id],"0") + "%");
												}
											});
										}else{
											tbodyObj.find("td[id]").text("0건");	
										}
									}else{
										tbodyObj.find("td[id]").text("0건");
									}
					            },
					            options : {
					                nomask : true
					            }
					        })
			        	});
			        	
			        },
		            options : {
		                nomask : true
		            }
		        })

			}catch(e){
				console.error("CTI_STAT",e)
			}
		}

		_ipccIntIds =  setInterval(function(){
					 callIpcc();
		},5000);
		
		callIpcc();
		return false;
	},
	CTI_STAT_DCI : function(caller, act, data){		
		var codeList = top.COMMON_CODE["MALL_ID"];		
		var tbodyObj = $("#callStatTbody");
		tbodyObj.empty();
		if(tbodyObj.length > 0) {
			trHtml = "";
			trHtml += '<tr style="height: 29px;">';
			trHtml += '<td style="border : 1px solid #fff;text-align:center;">엑스퍼</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="xper_inb_wait">0건</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="xper_inb_per">0%</td>';
			trHtml += '</tr>';
			trHtml += '<tr style="height: 29px;">';
			trHtml += '<td style="border : 1px solid #fff;text-align:center;">스마트웰컴</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="smtwelcom_inb_wait">0건</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="smtwelcom_inb_per">0%</td>';
			trHtml += '</tr>';
			trHtml += '<tr style="height: 29px;">';
			trHtml += '<td style="border : 1px solid #fff;text-align:center;">바이오숨</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="biosoom_inb_wait">0건</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="biosoom_inb_per">0%</td>';
			trHtml += '</tr>';
			trHtml += '<tr style="height: 29px;">';
			trHtml += '<td style="border : 1px solid #fff;text-align:center;">스마트웰</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="smtwel_inb_wait">0건</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="smtwel_inb_per">0%</td>';
			trHtml += '</tr>';
			trHtml += '<tr style="height: 29px;">';
			trHtml += '<td style="border : 1px solid #fff;text-align:center;">유리제로</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="glasszero_inb_wait">0건</td>';
			trHtml += '<td style="border : 1px solid #fff;text-align:right;padding:5px;" id="glasszero_inb_per">0%</td>';
			trHtml += '</tr>';
			tbodyObj.append($(trHtml));
		}
		
		var dataList = {};
		var _ipccIntIds = top.window._ipccIntIds;		
		
		console.info("_ipccIntIds",_ipccIntIds);
		
		if(!Util.isNothing(top.window._ipccIntIds)) clearInterval(_ipccIntIds);
		
		//운선생만.. cti 쪽 건드려도 되는데.. 공통이라 여기서 핸들링
		var callIpcc= function () {
			var url = "";
			if(location.protocol==='https:'){
		      	url = "https://" + SCRIPT_PROJECT.ipccUrl;
		    }else{
				url = "http://" + SCRIPT_PROJECT.ipccUrl;
		    }
			
			if(SCRIPT_SESSION["loginProjCd"] == "SAC"){
				url += "/call_logs?cmd=minidashinfo&center_id=11";
			}else if(SCRIPT_SESSION["loginProjCd"] == "SAC_DLI"){
				url += "/call_logs?cmd=minidashinfo&center_id=13";
			}else if(SCRIPT_SESSION["loginProjCd"] == "SAC_OLIT"){
				url += "/call_logs?cmd=minidashinfo&center_id=17";
			}else if(SCRIPT_SESSION["loginProjCd"] == "SAAS_DCI"){
				url += "/call_logs?cmd=minidash";
			}
			
			try{				
				var xmlhttp = new XMLHttpRequest();
				var method = "GET";
				
				xmlhttp.open(method, url, true);
				xmlhttp.onreadystatechange = () => {
					if (xmlhttp.readyState === XMLHttpRequest.DONE) {
						var status = xmlhttp.status;
						if (status === 0 || (status >= 200 && status < 400)) {
							data = JSON.parse(xmlhttp.responseText);
							if(data.result){
								var arr= data.data;
								if(arr.length > 0) {
									tbodyObj.find("td[id]").each(function(){
										var id= $(this).prop("id");
										var pos = id.indexOf('_');
										var queueName = id.substring(0,pos);
										
										for(var i=0;i<arr.length;i++){
											dataList = $.extend({},dataList, arr[i]);
											
											if(queueName == dataList.queue_name) {
												if(id == "xper_inb_wait") {
													tbodyObj.find("td").eq(1).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
												}
												if(id == "xper_inb_per") {												
													tbodyObj.find("td").eq(2).text(Util.nvl(String(dataList.connper),"0") + "%");
												}
												if(id == "smtwelcom_inb_wait") {
													tbodyObj.find("td").eq(4).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
												}
												if(id == "smtwelcom_inb_per") {												
													tbodyObj.find("td").eq(5).text(Util.nvl(String(dataList.connper),"0") + "%");
												}
												if(id == "biosoom_inb_wait") {
													tbodyObj.find("td").eq(7).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
												}
												if(id == "biosoom_inb_per") {												
													tbodyObj.find("td").eq(8).text(Util.nvl(String(dataList.connper),"0") + "%");
												}
												if(id == "smtwel_inb_wait") {
													tbodyObj.find("td").eq(10).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
												}
												if(id == "smtwel_inb_per") {												
													tbodyObj.find("td").eq(11).text(Util.nvl(String(dataList.connper),"0") + "%");
												}
												if(id == "glasszero_inb_wait") {
													tbodyObj.find("td").eq(13).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
												}
												if(id == "glasszero_inb_per") {												
													tbodyObj.find("td").eq(14).text(Util.nvl(String(dataList.connper),"0") + "%");
												}
											}
										}
									});
								}else{
									tbodyObj.find("td[id]").text("0건");	
								}
							}else{
								tbodyObj.find("td[id]").text("0건");
							}		
						} else { // 실패
							console.log("Error : " + xmlhttp.status);
						}
					}
				};
				xmlhttp.send();
				
//		        axboot.ajax({
//		        	type: "POST",
//			        url: ["callstat","selectMiniMon"],
//			        data: JSON.stringify({projCd : SCRIPT_SESSION["loginProjCd"],url : url}),
//			        callback: function(res) {			        	
//						if(res.map.result){
//							var arr= res.map.data;
//							if(arr.length > 0) {
//								tbodyObj.find("td[id]").each(function(){
//									var id= $(this).prop("id");
//									var pos = id.indexOf('_');
//									var queueName = id.substring(0,pos);
//									
//						        	for(var i=0;i<arr.length;i++){
//										dataList = $.extend({},dataList, arr[i]);
//										
//										if(queueName == dataList.queue_name) {
//											if(id == "xper_inb_wait") {
//												tbodyObj.find("td").eq(1).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
//											}
//											if(id == "xper_inb_per") {												
//												tbodyObj.find("td").eq(2).text(Util.nvl(String(dataList.connper),"0") + "%");
//											}
//											if(id == "smtwelcom_inb_wait") {
//												tbodyObj.find("td").eq(4).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
//											}
//											if(id == "smtwelcom_inb_per") {												
//												tbodyObj.find("td").eq(5).text(Util.nvl(String(dataList.connper),"0") + "%");
//											}
//											if(id == "biosoom_inb_wait") {
//												tbodyObj.find("td").eq(7).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
//											}
//											if(id == "biosoom_inb_per") {												
//												tbodyObj.find("td").eq(8).text(Util.nvl(String(dataList.connper),"0") + "%");
//											}
//											if(id == "smtwel_inb_wait") {
//												tbodyObj.find("td").eq(10).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
//											}
//											if(id == "smtwel_inb_per") {												
//												tbodyObj.find("td").eq(11).text(Util.nvl(String(dataList.connper),"0") + "%");
//											}
//											if(id == "glasszero_inb_wait") {
//												tbodyObj.find("td").eq(13).text(Util.nvl(String(dataList.waitcustom),"0") + "건");
//											}
//											if(id == "glasszero_inb_per") {												
//												tbodyObj.find("td").eq(14).text(Util.nvl(String(dataList.connper),"0") + "%");
//											}
//										}
//						        	}
//								});
//							}else{
//								tbodyObj.find("td[id]").text("0건");	
//							}
//						}else{
//							tbodyObj.find("td[id]").text("0건");
//						}
//			        },
//		            options : {
//		                nomask : true
//		            }
//		        })
			}catch(e){
				console.error("CTI_STAT_DCI",e)
			}
		}

		_ipccIntIds =  setInterval(function(){
					 callIpcc();
		},5000);
		
		callIpcc();
		return false;
	}
}));

// fnObj 기본 함수 스타트와 리사이즈
fnObj.pageStart = function () {
	
    window.onbeforeunload = null;
    
	var initMenu = 0; 
	var initMenuInfo = {};
	
	if(HOME_MENU_DATA.length > 0){
		var _homeTrees = ax5.util.convertList2Tree(HOME_MENU_DATA,{ childKey  : "menuCd",parentKey : "parentCd",labelKey  : "menuNm"});    
		axboot.def["DEFAULT_TAB_LIST"] = [].concat(_homeTrees);
	}
	
    var convertMenuItems = function(list){
        var _list = [];
        list.forEach(function (m) {
            var item = $.extend({}, m);
            if(item.hasChildren = (item.children && item.children.length)){
                item.children = convertMenuItems(item.children);
            }
            _list.push(item);
            if(axboot.def["DEFAULT_TAB_LIST"] == 0)
            {
	            if(!ax5.util.isNothing(item.program) && initMenu == 0){	            	
	            	initMenuInfo = $.extend({},item);            	
	            	initMenuInfo["url"] = item.program;
	            	initMenuInfo["status"] = "on";
	            	initMenuInfo["fixed"] = true;
	            	initMenu++;
	            }
            }
        });
        return _list;
    };
    
    var _menuTrees = ax5.util.convertList2Tree(TOP_MENU_DATA,{ childKey  : "menuCd",parentKey : "parentCd",labelKey  : "menuNm"});    
    this.menuItems = convertMenuItems(_menuTrees);
    
    if(this.menuItems && this.menuItems.length > 0){
	    this.menuItems[0].open = true;
	    if(initMenu > 0){	    
		    axboot.def["DEFAULT_TAB_LIST"] = [initMenuInfo];
	    }	
    }

    fnObj.frameView.initView();
    fnObj.tabView.initView();
    fnObj.pageButtonView.initView();

    $("[data-ax-path=loginProjCd]").change(function(){
        ACTIONS.dispatch(ACTIONS.CHANGE_PROJ);
	});
    
    ACTIONS.dispatch(ACTIONS.USER_MEMO);
};


fnObj.pageButtonView = axboot.viewExtend({
	initView: function () {
		axboot.buttonClick(this, "data-page-btn", {
			"logout": function () {
				ACTIONS.dispatch(ACTIONS.LOGOUT,true);
			},
			"saveMemo": function () {
                ACTIONS.dispatch(ACTIONS.SAVE_MEMO,false);
            },
            "delMemo": function () {
                ACTIONS.dispatch(ACTIONS.SAVE_MEMO,true);
            },
            "openMemo": function () {
                ACTIONS.dispatch(ACTIONS.USER_MEMO);
            }
		});
	}
});


fnObj.pageResize = function () {
    this.tabView.resize();
    if(_ipccYn == "Y"){
        axboot.layoutResize();
    }
};



fnObj.frameView = axboot.viewExtend({
    initView: function () {
        this.target = $("#ax-frame-root");
        this.asideHandle = $("#ax-aside-handel");
        this.aside = $("#ax-frame-aside");
        this.asideHandle.on("click", function () {
            ACTIONS.dispatch(ACTIONS.TOGGLE_ASIDE);
        });

        this.fullScreenHandle = $("#ax-fullscreen-handel");
        this.fullScreenHandle.on("click", function () {
            ACTIONS.dispatch(ACTIONS.TOGGLE_FULLSCREEN);
        });

        if (this.aside.get(0)) {
            this.asideView.initView();
            this.asideView.print();
            if(_ipccYn == "Y"){
                axboot.layoutResize();
                this.initEvent();
            }            
        }
    },
    toggleAside: function () {
        this.target.toggleClass("show-aside");
    },
    toggleFullScreen: function () {
        if (this.target.hasClass("full-screen")) {
            this.target.removeClass("full-screen");
        } else {
            this.target.addClass("full-screen");
            this.target.removeClass("show-aside");
        }

    },
    initEvent : function(){
        var timeIdx = "";
        this.target.find("[data-ax-path=memo]").keyup(function(e){
            var obj = $(this);
            var chgval = obj.val();
            var oriVal = obj.data("oriVal");
            
            if(chgval != oriVal){
                clearTimeout(timeIdx);
                timeIdx = setTimeout(function(){
                    obj.data("oriVal",chgval);
                    clearTimeout(timeIdx);
                    ACTIONS.dispatch(ACTIONS.SAVE_MEMO,false);
                },1000);
            }
        });
    },
    asideView: axboot.viewExtend({
        initView: function () {
            this.tmpl = $('[data-tmpl="ax-frame-aside"]').html();
        },
        print: function () {
            var menuItems = fnObj.menuItems;
            this.openedIndex = 0;
            fnObj.frameView.aside
                .html(ax5.mustache.render(this.tmpl, {items: menuItems}))
                .on("click", '[data-label-index]', function () {
                    var index = this.getAttribute("data-label-index");
                    if (menuItems[index].children && menuItems[index].children.length) {
                        fnObj.frameView.asideView.open(index);
                    } else {
                        if (menuItems[index].program) {
                            ACTIONS.dispatch(ACTIONS.MENU_OPEN, $.extend({},menuItems[index]));
                        }
                    }
                });
            
            $("#ax-frame-aside").find(".aside-link-nm").click(function(){
                var type   = $(this).attr("type");
                var target = $(this).attr("target");
                ACTIONS.dispatch(ACTIONS.CLICK_STATUS,{type : type, target : target});
            });
            
            //
            ACTIONS.dispatch(ACTIONS.DASH_SEARCH);
            if(SCRIPT_SESSION.loginProjCd == "SAC" || SCRIPT_SESSION.loginProjCd == "SAC_DLI" || SCRIPT_SESSION.loginProjCd == "SAC_OLIT"){
            	ACTIONS.dispatch(ACTIONS.CTI_STAT);
            } else if(SCRIPT_SESSION.loginProjCd == "SAAS_DCI"){
            	ACTIONS.dispatch(ACTIONS.CTI_STAT_DCI);
            }
            
            menuItems.forEach(function (n, nidx) {
                var $treeTarget = fnObj.frameView.aside.find('[data-tree-holder-index="' + nidx + '"]');
                if ($treeTarget.get(0)) {
                    var treeTargetId = $treeTarget.get(0).id;
                    $.fn.zTree.init(
                        $treeTarget,
                        {
                            view: {
                                dblClickExpand: false
                            },
                            callback: {
                                onClick: function (event, treeId, treeNode, clickFlag) {
                                    var zTree = $.fn.zTree.getZTreeObj(treeTargetId);
                                    if (treeNode.program) {
                                        
                                    	var menuNm   = treeNode.menuNm;
                                        var menuType = treeNode.menuType;
                                        var program  = treeNode.program;
                                        var menuCd   = treeNode.menuCd;
                                        
                                        if(menuType == "V"){                                        
                                        	ACTIONS.dispatch(ACTIONS.MENU_OPEN, $.extend({}, treeNode));
                                        }else if(menuType == "P"){
                                            var popConf = {id : menuCd};
                                            if(program in axboot.def["WINPOP"]){
                                                popConf = axboot.def["WINPOP"][program];
                                                popConf["popType"] = program;
                                            }else{
                                                popConf["url"] = program;
                                            }
                                            if(popConf.url.substr(0,4) == "http"){
                                            	popConf["url"]  = popConf["url"];
                                            	window.open(popConf["url"], '_blank');
//                                            	window.open(popConf["url"], '_blank', 'toolbar=yes, location=yes, status=yes, menubar=yes, scrollbars=yes')
                                            }else{
                                            	popConf["url"]  = popConf["url"] + "?menuCd=" + menuCd;
                                            	axboot.openWinPostPopup.open(popConf);
                                            }
                                            
                                        }else if(menuType == "M"){
                                        	var params = {modalType : program
                                        			     ,param     : {menuCd : menuCd} 
                                    	                 ,callback  : function(actFn,data){
                                    	                	 var fn = eval(actFn);
                                    	                	 if(ax5.util.isFunction(actFn)){
                                    	                		 fn(data);
                                    	                	 }
                                    	                 }
                                    		};		
                                    		ax5.util.openModal(params);	
                                        }
                                    }
                                    zTree.expandNode(treeNode);
                                }
                            }
                        },
                        n.children
                    );
                }
            });
        },
        open: function (_index) {
            if (this.openedIndex != _index) {

                fnObj.frameView.aside.find('[data-label-index="' + this.openedIndex + '"]').removeClass("opend");
                fnObj.frameView.aside.find('[data-tree-body-index="' + this.openedIndex + '"]').removeClass("opend");

                fnObj.frameView.aside.find('[data-label-index="' + _index + '"]').addClass("opend");
                fnObj.frameView.aside.find('[data-tree-body-index="' + _index + '"]').addClass("opend");

                this.openedIndex = _index;
            }
        },
        setDashData : function(data){
            
            var asidObj = $("#ax-frame-aside");
            var charcnt = 0;
            
            axToast.setConfig({
                theme: "danger",
                displayTime : 10000,
                closeIcon: '<i class="cqc-cancel3"></i>'
            });
            
            axToast.close();
            
            var i=1;
            for(var key in data){
                
                var val    = data[key];
                var msg    = "";
                
                var dataObj = asidObj.find("#"+key);
                var targetObj = dataObj.parent();
                var type   = targetObj.attr("type");
                var target = targetObj.attr("target");
                
                switch(key){
                    case "notice" :
                        msg    = "읽지 않은  공지사항이  "+val+"건 있습니다.";
                    break;
                    case "recall" :
                        msg    = "1시간 내에 재통화예약이 "+val+"건 있습니다.";
                    break;
                    case "callback" :
                        msg    = "미처리 콜백이 "+val+"건 있습니다.";
                    break;
                    case "tranfReq" :
                        msg    = "요청 접수"+val+"건 있습니다."
                    break;
                    case "inb_wait" :
                        msg    = "대기 콜 "+val+"건 있습니다."
                    break;
                    case "chat_wait" :
                        msg    = "대기 채팅 "+val+"건 있습니다."
                    break;
                    case "board_wait" :
                        msg    = "미답변 게시물 "+val+"건 있습니다."
                    break;
                    case "smsList" :
                        msg    = "모바일 CRM SMS "+val+"건 있습니다."
                        charcnt += parseInt(val);
                    break;
                    case "mmsList" :
                        msg    = "모바일 CRM MMS "+val+"건 있습니다."
                        charcnt += parseInt(val);
                    break;
                }

                if(SCRIPT_SESSION.loginProjCd == "SAC") {
                    if(key == "smsList" || key == "mmsList") {
                    	type = "";
                    	target = "";
                    	
                        if(val > 0 && !Util.isNothing(msg)) {
                            axToast.push({
                                msg: "<a style=\"color:#d9534f\" href=\"javascript:ACTIONS.dispatch(ACTIONS.CLICK_STATUS,{type : '"+type+"', target : '"+target+"',idx : "+i+"});\">"+msg+"</a>"
                            }, function () {
                            });
                            i++;
                        }
                    }                	
                } else {
                    if(dataObj.length > 0){
                        dataObj.text((val+"").lpad(2,"0"));
                        if(val > 0 && !Util.isNothing(msg)) {
                            axToast.push({
                                msg: "<a style=\"color:#d9534f\" href=\"javascript:ACTIONS.dispatch(ACTIONS.CLICK_STATUS,{type : '"+type+"', target : '"+target+"',idx : "+i+"});\">"+msg+"</a>"
                            }, function () {
                            });
                            i++;
                        }
                    }
                }
            }

        	asidObj.find("#charhis").text(String(charcnt).lpad(2,"0"));
        }
    })
});

/**
 * tabView
 */
fnObj.tabView = axboot.viewExtend({
    target: null,
    frameTarget: null,
    limitCount: 10,
    list : [],
    initView: function () {
    	
        this.target = $("#ax-frame-header-tab-container");
        //this.target.css("overflow","hidden");
        this.frameTarget = $("#content-frame-container");
        this.print();

        var menu = new ax5.ui.menu({
            position: "absolute", // default position is "fixed"
            theme: "primary",
            icons: {
                'arrow': '▸'
            },
            items: [
                {icon: '<i class="cqc-ccw"></i>'    , label: MSG("label.common.curtabrefresh"), action: "reload"},
                {icon: '<i class="cqc-cancel3"></i>', label: MSG("label.common.curtabclose"), action: "close"},
                {icon: '<i class="cqc-cancel"></i>' , label: MSG("label.common.curtabexpclose"), action: "closeAnother"},
                {icon: '<i class="cqc-cancel"></i>' , label: MSG("label.common.tabcloseall"), action: "closeAll"}
            ]
        });

        menu.onClick = function () {
            switch (this.action) {
                case "reload":
                    fnObj.tabView.list.forEach(function (_item, idx) {
                        if (_item.status == "on") {
                            window["frame-item-" + _item.menuCd].location.reload();
                            return false;
                        }
                    });
                    break;
                case "close":
                    fnObj.tabView.list.forEach(function (_item, idx) {
                        if (_item.status == "on") {                            
                            fnObj.tabView.close(_item.menuCd);
                            return false;
                        }
                    });
                    break;
                case "closeAnother":
                    fnObj.tabView.list.forEach(function (_item, idx) {
                        if (idx > 0 && _item.status != "on") {
                            fnObj.tabView.close(_item.menuCd);
                        }
                    });
                    //fnObj.tabView.open(fnObj.tabView.list[0]);
                    break;
                case "closeAll":
                    fnObj.tabView.list.forEach(function (_item, idx) {
                        if (idx > 0) {
                            fnObj.tabView.close(_item.menuCd);
                        }
                    });
                    fnObj.tabView.open(fnObj.tabView.list[0]);
                    break;
                default:
                    return false;
            }
        };

        this.target.on("contextmenu", '.tab-item', function (e) {
            menu.popup(e);
            ax5.util.stopEvent(e);
        });
    },
    _getItem: function (item) {
        var po = [];
        var menuGroup = ax5.util.nvl(item["menuGroup"]);
        
        po.push('<div class="tab-item ' + item.status + '" data-tab-id="' + item.menuCd + '" menugroup="'+menuGroup+'">');
        po.push('<span data-toggle="tooltip" data-placement="bottom" title=\'' + item.menuNm + '\'>', item.menuNm, '</span>');
        if (!item.fixed) po.push('<i class="cqc-cancel3" data-tab-close="true" data-tab-id="' + item.menuCd + ' "></i>');
        po.push('</div>');
        return po.join('');
    },
    _getFrame: function (item) {
        var po = [];
        var menuGroup = ax5.util.nvl(item["menuGroup"]);
        var load   = item["load"];
        if(menuGroup == "home" ||  menuGroup == "chat") {
            if(load){
                po.push('<iframe onLoad="fnObj.tabView.load(this)" class="frame-item ' + item.status + '" data-tab-id="' + item.menuCd + '" name="frame-item-' + item.menuCd + '" src="' + item.url + '" menugroup="'+menuGroup+'" frameborder="0" framespacing="0"></iframe>');
            }else{
                po.push('<iframe onLoad="fnObj.tabView.load(this)" class="frame-item ' + item.status + '" data-tab-id="' + item.menuCd + '" name="frame-item-' + item.menuCd + '" data-src="' + item.url + '" menugroup="'+menuGroup+'" frameborder="0" framespacing="0"></iframe>');
            }
        }else{
            po.push('<iframe onLoad="fnObj.tabView.load(this)" class="frame-item ' + item.status + '" data-tab-id="' + item.menuCd + '" name="frame-item-' + item.menuCd + '" src="' + item.url + '" menugroup="'+menuGroup+'" frameborder="0" framespacing="0"></iframe>');
        }
        return po.join('');
    },
    load : function(obj){
        var menugroup = $(obj).attr("menugroup");
        if(menugroup != "home"){
            axAJAXMask.close(300);
        }
    },
    print: function () {
        var _this = this;

        var po = [], fo = [], active_item;

/*        po.push('<div class="tab-item-holder">');
        po.push('<div class="tab-item-menu" data-tab-id="" style="display: block;width: 37px !important;cursor: pointer;border: 1px solid #333 !important;height: 27px;text-align: center;">');
        po.push('<button style="width: 100%;height: 100%;border: 0px;left: 0px;padding-left: 1px;">&lt;</button>');
        po.push('</div>');
        this.list.forEach(function (_item, idx) {
            po.push(_this._getItem(_item));
            fo.push(_this._getFrame(_item));
            if (_item.status == "on") {
                active_item = _item;
            }
        });
        po.push('<div class="tab-item-addon" data-tab-id="" style="position: absolute;right: 0px;width: 37px;cursor: pointer;border: 1px solid #333;height: 27px;text-align: center;">');
        po.push('<button style="width: 100%;height: 100%;border: 0px;left: 0px;padding-left: 3px;">&gt;</button>');
        po.push('</div>');
        po.push('</div>');*/

        po.push('<div class="tab-item-holder">');
        po.push('<div class="tab-item-menu" data-tab-id="">');
        po.push('</div>');
        this.list.forEach(function (_item, idx) {
            po.push(_this._getItem(_item));
            fo.push(_this._getFrame(_item));
            if (_item.status == "on") {
                active_item = _item;
            }
        });
        po.push('<div class="tab-item-addon" data-tab-id="" >');
        po.push('</div>');
        po.push('</div>');
        
        this.target.html(po.join(''));
        this.frameTarget.html(fo.join(''));
        this.targetHolder = this.target.find(".tab-item-holder");
        // event bind
        this.bindEvent();

        if(axboot.def["DEFAULT_TAB_LIST"].length > 0) {
        	var defaultMenuTabList = axboot.def["DEFAULT_TAB_LIST"]; 
        	for(var i=0;i<defaultMenuTabList.length;i++){
        		var defaultMenuInfo  = defaultMenuTabList[i];
        		defaultMenuInfo["fixed"] = true;
        		if(i == defaultMenuTabList.length -1 ){
        		    defaultMenuInfo["load"]  = true;
        		}else{
        		    defaultMenuInfo["load"]  = false;
        		}
        		fnObj.tabView.open(defaultMenuInfo);
        	}
    	}
    },
    open: function (item) {
        
    	var _item;
        var load  = ax5.util.nvl(item["load"],true);
        var subInfo = item["subInfo"];
        
        var findedIndex = ax5.util.search(this.list, function () {
            this.status = '';
            return this.menuCd == item.menuCd;
        });
        
        if(load){
        	this.target.find('.tab-item').removeClass("on");        
        	this.frameTarget.find('.frame-item').removeClass("on");
        }
        
        if (findedIndex < 0) {
        	
        	var progPath = CONTEXT_PATH + item.program;
			var menuCd = (item.menuGroup == "chat") ? item.subMenuCd : item.menuCd;
        	if(progPath.indexOf("?") > -1){
        		progPath = progPath + "&menuCd=" + menuCd;
        	}else{
        		progPath = progPath + "?menuCd=" + menuCd;
        	}

        	_item = {
                    menuCd: item.menuCd,
                    id: item.id,
                    progNm: item.progNm,
                    menuNm: item.menuNm,
                    progPh: item.program,
                    url: progPath,
                    menuGroup : item.menuGroup,
                    fixed  : item.fixed,
                    status: ax5.util.nvl(item["status"],"on"),
                    load   : item["load"]
                }
            this.list.push(_item);
            this.targetHolder.find(".tab-item-addon").before(this._getItem(_item));
            
            
            //if(item["load"]){
            var menuFrmObj = this._getFrame(_item);
            this.frameTarget.append(menuFrmObj);

			//console.info("load => "+load,_item);
			
            if(load){
	            var menugroup = $(menuFrmObj).attr("menugroup");
	            if((menugroup == "home" && menugroup == "chat")){
            		axAJAXMask.open();
	            }
            }
            if(!Util.isNothing(item.menuCd) && !Util.isNothing(subInfo)){
            	window["MENU_"+item.menuCd] = subInfo;
            }
            //}
        }
        else {
	        this.target.find('.tab-item').removeClass("on");
	        this.frameTarget.find('.frame-item').removeClass("on");
            _item = this.list[findedIndex];
            this.target.find('[data-tab-id="' + _item.menuCd + '"]').addClass("on");
            this.frameTarget.find('[data-tab-id="' + _item.menuCd + '"]').addClass("on");
        }
        if (_item) {
            //topMenu.setHighLightOriginID(_item.menuCd || "");
        }

        /*if (this.list.length > this.limitCount) {
            this.close(this.list[1].menuCd);
        }*/

        this.bindEvent();
        this.resize();
    },
    click: function (id, e) {   	
        this.list.forEach(function (_item) {
            if (_item.menuCd == id) {
                _item.status = 'on';
                if(e){
                    if (e.shiftKey) {
                        window.open(_item.url);
                    }
                }
                if (_item) {
                    //topMenu.setHighLightOriginID(_item.menuCd || "");
                }
            }
            else _item.status = '';
        });
        var tabAllObj = this.target.find('.tab-item');
        var frmAllObj = this.frameTarget.find('.frame-item');
        
        tabAllObj.removeClass("on");
        frmAllObj.removeClass("on");
        
        var tabObj = this.target.find('[data-tab-id="' + id + '"]');
        var frmObj = this.frameTarget.find('[data-tab-id="' + id + '"]');

        tabObj.removeClass("blink");
        frmObj.removeClass("blink");
        
        tabObj.addClass("on");
        frmObj.addClass("on");
        
        var menuGroup = frmObj.attr("menuGroup");
        if(menuGroup == "home" || menuGroup == "chat"){
            if(frmObj.data("src") && Util.nvl(frmObj.attr("src")) == ""){
                frmObj.attr("src",frmObj.data("src"));
                frmObj.data("src",null);
                //delete frmObj.data("src");
            }
        }
        if(frmObj) {
        	var frmResize = function(frm){
        		if(frm.axboot){
        			frm.axboot.pageResize();
        			frm.axboot.pageAutoHeight.align();
        			if(frm.fnObj){
	        			if(frm.fnObj.pageResize){
	        				frm.fnObj.pageResize();
	        			}
        			}
 	           }
        	}
        	var tabFrmObj = frmObj[0].contentWindow;
        	frmResize(tabFrmObj);
        	var childFrmObjs = $(tabFrmObj.document).find("iframe");
        	if(childFrmObjs.length > 0){
        		childFrmObjs.each(function(){
        			frmResize($(this)[0].contentWindow);
        		});
        	}
        }
    },
    close: function (menuCd) {
        var newList = [], removeItem;
        this.list.forEach(function (_item) {
            if (_item.menuCd != menuCd) newList.push(_item);
            else removeItem = _item;
        });
        
        if (newList.length == 0) {
            axDialog.alert(MSG("message.validate.notclosetab"));
            return false;
        }
        this.list = newList;
        var tabTitleObj = this.target.find('[data-tab-id="' + menuCd + '"]');
        var menuGroup = tabTitleObj.attr("menugroup");
        
        //채팅 방을 닫을때.. room 세션에서 제외시켜주는 로직 담당상담원은 제외
        if(menuGroup == "chat") {
        	var userCd   = SCRIPT_SESSION['userCd'];
        	var chatInfo = window["MENU_"+menuCd];
        	if(userCd != chatInfo["userCd"]){
        		top.fnChat.activityView.clearUser(Util.deepCopy(chatInfo));
        	}
        	delete window["MENU_"+menuCd];
        }
        tabTitleObj.remove();        
        
        // 프레임 제거
        (function () {
            var $iframe = this.frameTarget.find('[data-tab-id="' + menuCd + '"]'), // iframe jQuery Object
                iframeObject = $iframe.get(0),
                idoc = (iframeObject.contentDocument) ? iframeObject.contentDocument : iframeObject.contentWindow.document;

            $(idoc.body).children().each(function () {
                $(this).remove();
            });
            idoc.innerHTML = "";
            $iframe
                .attr('src', 'about:blank')
                .remove();

            // force garbarge collection for IE only
            window.CollectGarbage && window.CollectGarbage();
        }).call(this);

        if (tabTitleObj.hasClass("on")) {
            var lastIndex = this.list.length - 1;
 			var clickTabObj = this.target.find('.tab-item')[lastIndex];
            clickTabObj.click();
          /*  var frameTargetObj = this.frameTarget.find('[data-tab-id="' + menuCd + '"]');
            this.list[lastIndex].status = 'on';
            var cTitleObj = this.target.find('[data-tab-id="' + menuCd + '"]');
            cTitleObj.addClass("on");
            if(cTitleObj.hasClass("blink")){
            	cTitleObj.removeClass("blink")
            }*/
            
            /*if(frameTargetObj.data("src")){
            	if(ax5.util.isNothing(frameTargetObj.attr("src"))){*/
            		/*var menuInfo = null;
            		var mList = this.list;
            		for(var i=0;i<mList.length;i++){
            			menuInfo = mList[i];
            			if(menuInfo.menuCd == menuCd) {
            				
        	            	break;
            			}
            		}*/
            /*	}
            }*/
        }

        // check status = "o0n"
        /*var hasStatusOn = false;
        this.list.forEach(function (_item) {
            if (_item.status == "on") hasStatusOn = true;
        });
        if (!hasStatusOn) {
            var lastIndex = this.list.length - 1;
            this.list[lastIndex].status = 'on';
            this.target.find('[data-tab-id="' + this.list[lastIndex].menuCd + '"]').addClass("on");
            this.frameTarget.find('[data-tab-id="' + this.list[lastIndex].menuCd + '"]').addClass("on");
        }*/
        this.target.find('.tooltip').remove();
        this.resize();
    },
    bindEvent: function () {
        var _this = this;
        this.target.find('.tab-item').unbind("click").bind("click", function (e) {
            if (e.target.tagName == "I") {
                _this.close(this.getAttribute("data-tab-id"));
            }
            else {
                _this.click(this.getAttribute("data-tab-id"), e);
            }
        });
        this.target.find('[data-toggle="tooltip"]').tooltip();
    },
    resize: function () {
        if (this.resizeTimer) clearTimeout(this.resizeTimer);
        this.resizeTimer = setTimeout((function () {
            var ctWidth = this.target.width();
            var tabsWidth = this.targetHolder.outerWidth();

            if (ctWidth < tabsWidth) {
                this.targetHolder.css({width: "100%"});
                this.target.find('.tab-item').css({'min-width': 'auto', width: (ctWidth / this.list.length) - 4});
            }
            else {
                this.targetHolder.css({width: "auto"});
                this.target.find('.tab-item').css({'min-width': '120px', width: "auto"});
                tabsWidth = this.targetHolder.outerWidth();
                if (ctWidth < tabsWidth) {
                    this.targetHolder.css({width: "100%"});
                    this.target.find('.tab-item').css({'min-width': 'auto', width: (ctWidth / this.list.length) - 4});
                }
            }
        }).bind(this), 100);
    }
});
