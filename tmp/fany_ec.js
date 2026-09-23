/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	// The require scope
/******/ 	var __webpack_require__ = {};
/******/
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => module['default'] :
/******/ 				() => module;
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => Object.prototype.hasOwnProperty.call(obj, prop)
/******/ 	})();
/******/
/************************************************************************/

// CONCATENATED MODULE: external "Handlebars"
const external_Handlebars_namespaceObject = Handlebars;
var external_Handlebars_default = /*#__PURE__*/__webpack_require__.n(external_Handlebars_namespaceObject);
// CONCATENATED MODULE: external "_"
const external_namespaceObject = _;
var external_default = /*#__PURE__*/__webpack_require__.n(external_namespaceObject);
// CONCATENATED MODULE: ./node_modules/throttle-debounce/esm/index.js
/* eslint-disable no-undefined,no-param-reassign,no-shadow */

/**
 * Throttle execution of a function. Especially useful for rate limiting
 * execution of handlers on events like resize and scroll.
 *
 * @param  {number}    delay -          A zero-or-greater delay in milliseconds. For event callbacks, values around 100 or 250 (or even higher) are most useful.
 * @param  {boolean}   [noTrailing] -   Optional, defaults to false. If noTrailing is true, callback will only execute every `delay` milliseconds while the
 *                                    throttled-function is being called. If noTrailing is false or unspecified, callback will be executed one final time
 *                                    after the last throttled-function call. (After the throttled-function has not been called for `delay` milliseconds,
 *                                    the internal counter is reset).
 * @param  {Function}  callback -       A function to be executed after delay milliseconds. The `this` context and all arguments are passed through, as-is,
 *                                    to `callback` when the throttled-function is executed.
 * @param  {boolean}   [debounceMode] - If `debounceMode` is true (at begin), schedule `clear` to execute after `delay` ms. If `debounceMode` is false (at end),
 *                                    schedule `callback` to execute after `delay` ms.
 *
 * @returns {Function}  A new, throttled, function.
 */
function throttle (delay, noTrailing, callback, debounceMode) {
  /*
   * After wrapper has stopped being called, this timeout ensures that
   * `callback` is executed at the proper times in `throttle` and `end`
   * debounce modes.
   */
  var timeoutID;
  var cancelled = false; // Keep track of the last time `callback` was executed.

  var lastExec = 0; // Function to clear existing timeout

  function clearExistingTimeout() {
    if (timeoutID) {
      clearTimeout(timeoutID);
    }
  } // Function to cancel next exec


  function cancel() {
    clearExistingTimeout();
    cancelled = true;
  } // `noTrailing` defaults to falsy.


  if (typeof noTrailing !== 'boolean') {
    debounceMode = callback;
    callback = noTrailing;
    noTrailing = undefined;
  }
  /*
   * The `wrapper` function encapsulates all of the throttling / debouncing
   * functionality and when executed will limit the rate at which `callback`
   * is executed.
   */


  function wrapper() {
    for (var _len = arguments.length, arguments_ = new Array(_len), _key = 0; _key < _len; _key++) {
      arguments_[_key] = arguments[_key];
    }

    var self = this;
    var elapsed = Date.now() - lastExec;

    if (cancelled) {
      return;
    } // Execute `callback` and update the `lastExec` timestamp.


    function exec() {
      lastExec = Date.now();
      callback.apply(self, arguments_);
    }
    /*
     * If `debounceMode` is true (at begin) this is used to clear the flag
     * to allow future `callback` executions.
     */


    function clear() {
      timeoutID = undefined;
    }

    if (debounceMode && !timeoutID) {
      /*
       * Since `wrapper` is being called for the first time and
       * `debounceMode` is true (at begin), execute `callback`.
       */
      exec();
    }

    clearExistingTimeout();

    if (debounceMode === undefined && elapsed > delay) {
      /*
       * In throttle mode, if `delay` time has been exceeded, execute
       * `callback`.
       */
      exec();
    } else if (noTrailing !== true) {
      /*
       * In trailing throttle mode, since `delay` time has not been
       * exceeded, schedule `callback` to execute `delay` ms after most
       * recent execution.
       *
       * If `debounceMode` is true (at begin), schedule `clear` to execute
       * after `delay` ms.
       *
       * If `debounceMode` is false (at end), schedule `callback` to
       * execute after `delay` ms.
       */
      timeoutID = setTimeout(debounceMode ? clear : exec, debounceMode === undefined ? delay - elapsed : delay);
    }
  }

  wrapper.cancel = cancel; // Return the wrapper function.

  return wrapper;
}

/* eslint-disable no-undefined */
/**
 * Debounce execution of a function. Debouncing, unlike throttling,
 * guarantees that a function is only executed a single time, either at the
 * very beginning of a series of calls, or at the very end.
 *
 * @param  {number}   delay -         A zero-or-greater delay in milliseconds. For event callbacks, values around 100 or 250 (or even higher) are most useful.
 * @param  {boolean}  [atBegin] -     Optional, defaults to false. If atBegin is false or unspecified, callback will only be executed `delay` milliseconds
 *                                  after the last debounced-function call. If atBegin is true, callback will be executed only at the first debounced-function call.
 *                                  (After the throttled-function has not been called for `delay` milliseconds, the internal counter is reset).
 * @param  {Function} callback -      A function to be executed after delay milliseconds. The `this` context and all arguments are passed through, as-is,
 *                                  to `callback` when the debounced-function is executed.
 *
 * @returns {Function} A new, debounced function.
 */

function debounce (delay, atBegin, callback) {
  return callback === undefined ? throttle(delay, atBegin, false) : throttle(delay, callback, atBegin !== false);
}



// CONCATENATED MODULE: external "Swiper"
const external_Swiper_namespaceObject = Swiper;
var external_Swiper_default = /*#__PURE__*/__webpack_require__.n(external_Swiper_namespaceObject);
// CONCATENATED MODULE: ./src/assets/js/util.ts
// =jQuery(selector, context)
function getOne(selector, context) {
    if (context === void 0) { context = document; }
    if (selector instanceof HTMLElement) {
        return selector;
    }
    return context.querySelector(selector);
}
// =jQuery(selector, context)
function getAll(selector, context) {
    if (context === void 0) { context = document; }
    var nodes = context.querySelectorAll(selector);
    return Array.from(nodes);
}
// =jQuery(el).siblings()
function getSiblings(el) {
    return Array.prototype.filter.call(el.parentElement.children, function (child) { return child !== el; });
}
// =jQuery(el).css(name)
function getStyle(el, name) {
    var declaration = el.ownerDocument.defaultView.getComputedStyle(el, null);
    return declaration.getPropertyValue(name);
}
// =jQuery(el).offset()
function getOffset(el) {
    var _a = el.getBoundingClientRect(), top = _a.top, left = _a.left;
    var pageYOffset = window.pageYOffset, pageXOffset = window.pageXOffset;
    var _b = document.documentElement, clientTop = _b.clientTop, clientLeft = _b.clientLeft;
    return {
        top: top + pageYOffset - clientTop,
        left: left + pageXOffset - clientLeft,
    };
}
// =jQuery(el).trigger(name)
function dispatchEvent(el, name, detail) {
    var event = new CustomEvent(name, {
        detail: detail,
        bubbles: true,
        cancelable: true,
    });
    el.dispatchEvent(event);
}
// =jQuery(document).on(type, selector, listener)
function delegate(type, selector, listener, useCapture) {
    if (useCapture === void 0) { useCapture = false; }
    var handler = function (e) {
        if (e.target === document) {
            return;
        }
        var context = e.target.closest(selector);
        if (context) {
            listener.call(context, e);
        }
    };
    document.addEventListener(type, handler, useCapture);
}
// =_.forEach(obj, fn)
function forOf(obj, fn) {
    Object.keys(obj).forEach(function (key) { return fn.call(null, obj[key], key); });
}
// Return width of browser's scroll bar
function getScrollBarWidth() {
    var div = document.createElement('div');
    div.style.position = 'absolute';
    div.style.overflowY = 'scroll';
    document.body.appendChild(div);
    var w = div.offsetWidth;
    document.body.removeChild(div);
    return w;
}
// Return whether browser's  scroll bar is visible or not
function isScrollBarVisible() {
    return document.body.scrollHeight > document.body.clientHeight;
}
// =jQuery(window).scrollTop();
function getScrollTop() {
    return ((document.documentElement && document.documentElement.scrollTop) ||
        document.body.scrollTop);
}
// Parse URL query strings
function parseQuery() {
    var data = new Map();
    var queryStr = window.location.search.substr(1);
    queryStr.split('&').forEach(function (q) {
        if (!q) {
            return;
        }
        var _a = q.split('='), key = _a[0], _b = _a[1], value = _b === void 0 ? true : _b;
        if (!data.has(key)) {
            data.set(key, []);
        }
        data.get(key).push(value);
    });
    return data.size === 0 ? undefined : data;
}
// =_.uniq(array)
function uniq(array) {
    var set = new Set(array);
    return Array.from(set);
}
// Toggle a state of the page
function toggleState(stateStr, on) {
    var _a;
    var el = getOne('html');
    var states = stateStr.trim().split(/\s+/);
    var currentStates = ((_a = el.dataset.states) !== null && _a !== void 0 ? _a : '').trim().split(/\s+/);
    if (on) {
        currentStates.push.apply(currentStates, states);
    }
    else {
        currentStates = currentStates.filter(function (s) { return !states.includes(s); });
    }
    currentStates = uniq(currentStates);
    el.dataset.states = currentStates.join(' ').trim();
}
// Check a state of the page
function hasState(state) {
    return getOne('html').matches("[data-states~=\"" + state + "\"]");
}
// Format number as price
function formatNumberAsPrice(num) {
    var s = String(num).split('.');
    var str = String(s[0]).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,');
    if (s.length > 1) {
        str += '.' + s[1];
    }
    return str;
}
// Returns a debounced function
function util_debounce(callback, wait) {
    var id;
    return function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        window.clearTimeout(id);
        id = window.setTimeout(function () { return callback.apply(void 0, args); }, wait);
    };
}
// clip the entire page
function clipPage(clip) {
    var isClipped = hasState('clip');
    if ((isClipped && clip) || (!isClipped && !clip)) {
        return;
    }
    var page = getOne('.g-wrapper');
    if (clip) {
        var y = getScrollTop();
        toggleState('clip', true);
        page.scrollTop = y;
    }
    else {
        var y = page.scrollTop;
        toggleState('clip', false);
        window.scrollTo(0, y);
    }
}

// CONCATENATED MODULE: ./src/assets/js/carousel.ts
;

var Carousel = /** @class */ (function () {
    function Carousel(selector) {
        this.el = getOne(selector);
    }
    Carousel.prototype.toggleClasses = function (on) {
        var wrapper = this.el.children[0];
        var slides = Array.from(wrapper.children);
        this.el.classList.toggle('swiper-container', on);
        wrapper.classList.toggle('swiper-wrapper', on);
        slides.forEach(function (el) { return el.classList.toggle('swiper-slide', on); });
    };
    Carousel.prototype.init = function (options) {
        this.destroy();
        this.toggleClasses(true);
        this.swiper = new (external_Swiper_default())(this.el, options);
    };
    Carousel.prototype.destroy = function () {
        if (this.swiper) {
            this.swiper.destroy();
            this.swiper = undefined;
            this.toggleClasses(false);
        }
    };
    return Carousel;
}());


// CONCATENATED MODULE: ./src/assets/js/ec.ts
var __assign = (undefined && undefined.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};





external_Handlebars_default().registerHelper('noPriority', function () { return window.ORDER_LIMIT === 1; });
external_Handlebars_default().registerHelper('is_lottery', function () { return window.IS_LOTTERY; });
external_Handlebars_default().registerHelper('hasKind', function () { return window.ORDER_KIND; });
external_Handlebars_default().registerHelper('format', function (str) { return Number(str).toLocaleString(); });
external_Handlebars_default().registerHelper('format2', function (str, amount) {
    var num = +str * +amount;
    return num.toLocaleString();
});
external_Handlebars_default().registerHelper('math', function (left, operator, right) {
    left = parseFloat(left);
    right = parseFloat(right);
    var MATH = {
        '+': left + right,
        '-': left - right,
        '*': left * right,
        '/': left / right,
        '%': left % right,
    };
    return MATH[operator];
});
external_Handlebars_default().registerHelper('ticketTotal', function () { return Number(ticketTotal).toLocaleString(); });
external_Handlebars_default().registerHelper('discount', function () { return window.DISCOUNT_DATA.length > 0; });
external_Handlebars_default().registerHelper('paymentPrice', function () {

    if (window.COMMISSION != undefined) {
        var service_commission = typeof window.COMMISSION.service === 'undefined' ? 0 : window.COMMISSION.service;
        var system_commission = typeof window.COMMISSION.system === 'undefined' ? 0 : window.COMMISSION.system;
        if (window.PAYMENT_CODE != undefined) {
            var payment_commission = typeof window.COMMISSION.payment['0'+window.PAYMENT_CODE] === 'undefined' ? 0 : window.COMMISSION.payment['0'+window.PAYMENT_CODE];
        } else {
            var payment_commission = typeof window.COMMISSION.payment[payment_code] === 'undefined' ? 0 : window.COMMISSION.payment[payment_code];
        }
        if (window.RECEIPT_CODE != undefined) {
            var receive_commission = typeof window.COMMISSION.receipt[window.RECEIPT_CODE] === 'undefined' ? 0 : window.COMMISSION.receipt[window.RECEIPT_CODE];
        } else {
            var receive_commission = typeof window.COMMISSION.receipt[receipt_code] === 'undefined' ? 0 : window.COMMISSION.receipt[receipt_code];
        }
    } else {
        var service_commission = 0;
        var system_commission = 0;
        var payment_commission = 0;
        var receive_commission = 0;
    }
    var total_commission = service_commission + system_commission + payment_commission + receive_commission;

    var discount_price = 0;
    if (window.DISCOUNT_DATA.length > 0) {
        for (let i = 0; i < window.DISCOUNT_DATA.length; i++) {
            if (window.DISCOUNT_DATA[i]['is_display']) {
                discount_price += Number(window.DISCOUNT_DATA[i]['apply_price']);
            }
        }
    }

    var payment_price = ticketTotal + total_commission - discount_price;
    return Number(payment_price).toLocaleString();
});
external_Handlebars_default().registerHelper('before_discount', function (index) {
    if (window.COMMISSION != undefined) {
        var service_commission = typeof window.COMMISSION.service === 'undefined' ? 0 : window.COMMISSION.service;
        var system_commission = typeof window.COMMISSION.system === 'undefined' ? 0 : window.COMMISSION.system;
        if (window.PAYMENT_CODE != undefined) {
            var payment_commission = typeof window.COMMISSION.payment['0'+window.PAYMENT_CODE] === 'undefined' ? 0 : window.COMMISSION.payment['0'+window.PAYMENT_CODE];
        } else {
            var payment_commission = typeof window.COMMISSION.payment[payment_code] === 'undefined' ? 0 : window.COMMISSION.payment[payment_code];
        }
        var receive_commission = typeof window.COMMISSION.receipt[receipt_code] === 'undefined' ? 0 : window.COMMISSION.receipt[receipt_code];
    } else {
        var service_commission = 0;
        var system_commission = 0;
        var payment_commission = 0;
        var receive_commission = 0;
    }

    var sum_discount_price = 0;
    if (index > 0) {
        for (let i = 0; i < index; i++) {
            if (window.DISCOUNT_DATA[i]['is_display']) {
                sum_discount_price += window.DISCOUNT_DATA[i]['apply_price'];
            }
        }
    }

    var total_commission = service_commission + system_commission + payment_commission + receive_commission;
    beforeDiscountPrice = ticketTotal + total_commission - sum_discount_price;
    return Number(beforeDiscountPrice).toLocaleString();
});
external_Handlebars_default().registerHelper('after_discount', function (str) {
    var after_discount_price = beforeDiscountPrice - Number(str);
    return Number(after_discount_price).toLocaleString();
});
external_Handlebars_default().registerHelper('check_tabs_length', function (data) {
    return data.length > 1;
});

var kinds = ['live', 'goods', 'set'];
function getTmpl(id) {
    var elm = getOne("#" + id);
    if (elm) {
        var source = elm.innerHTML;
        return external_Handlebars_default().compile(source);
    }
    return false;
}
var rowTmpls = {
    live: getTmpl('tmplLiveTableRow'),
    goods: getTmpl('tmplGoodsTableRow'),
    set: getTmpl('tmplSetTableRow'),
};
var tableTmpls = {
    live: getTmpl('tmplLiveTable'),
    goods: getTmpl('tmplGoodsTable'),
    set: getTmpl('tmplSetTable'),
};
var tabTmpl = getTmpl('tmplTab');
var tabSetTmpl = getTmpl('tmplTabSet');
var ticketTotal = 0;
var beforeDiscountPrice = 0;
function handleData(kind, dataSet) {
    var subtotal = 0;
    var rows = '';
    dataSet.forEach(function (data) {
        rows += rowTmpls[kind](data);
        subtotal += data.price * data.amount;
    });
    var html = tableTmpls[kind]({ rows: rows, subtotal: subtotal });
    return { html: html, subtotal: subtotal };
}
function toggleTabsShadow(swiper) {
    swiper.el.classList.toggle('g-total_headWrapper-lead', swiper.isBeginning);
    swiper.el.classList.toggle('g-total_headWrapper-tail', swiper.isEnd);
}
function resetSlidesPerGroup(swiper) {
    // destroyされた直後にコールされた場合
    if (!swiper.wrapperEl) {
        return;
    }
    var slide = swiper.slides[0];
    // 非表示要素のSwiperの場合
    if (!slide) {
        return;
    }
    var mr = parseInt(slide.style.marginRight, 10);
    var slidesPerGroup = Math.floor((swiper.wrapperEl.offsetWidth + mr) / (slide.offsetWidth + mr));
    swiper.params.slidesPerGroup = slidesPerGroup;
    swiper.update();
}
function makeTabsSlidable() {
    getAll('.g-total_headWrapper').forEach(function (el) {
        var carousel = new Carousel(el);
        carousel.init({
            slidesPerView: 'auto',
            spaceBetween: 5,
            freeMode: true,
            navigation: {
                nextEl: getOne('.g-total_next', el.parentNode),
                prevEl: getOne('.g-total_prev', el.parentNode),
            },
            on: {
                init: function (swiper) {
                    toggleTabsShadow(swiper);
                    resetSlidesPerGroup(swiper);
                },
                resize: debounce(500, resetSlidesPerGroup),
                toEdge: function (swiper) {
                    toggleTabsShadow(swiper);
                },
                fromEdge: function (swiper) {
                    toggleTabsShadow(swiper);
                },
                click: function (swiper, e) {
                    if (e.target instanceof HTMLButtonElement) {
                        window.__handleTab.apply(e.target);
                    }
                },
            },
        });
    });
}
function updateTabsByJson() {
    var is_multiple = true;
    if (typeof window.IS_LOTTERY !== 'undefined' && typeof window.IS_MULTIPLE !== 'undifined') {
        if (window.IS_LOTTERY === true && window.IS_MULTIPLE === false) {
            is_multiple = false;
        }
    }
    ticketTotal = 0;
    var sortedOrderData = window.ORDER_DATA;
    if (!window.IS_LOTTERY) {
        if(typeof sortedOrderData[0] !== 'undefined' && ("live") in sortedOrderData[0] == true){
            const dd = sortedOrderData[0]['live']
            dd.sort(function(a, b) {
                return a.performance_display_order - b.performance_display_order;

            });
        }
    }
    var tabs = sortedOrderData.map(function (orderData, i) {
        var res = { priority: i, total: 0 };
        var tabData = kinds.reduce(function (map, kind) {
            var dataSet = orderData[kind];
            if (dataSet) {
                var data = dataSet.filter(function (d){
                    return d.amount != 0;
                    });

                var _a = handleData(kind, data), html_1 = _a.html, subtotal = _a.subtotal;
                map[kind] = html_1;
                res.total += subtotal;
                if (is_multiple) {
                    ticketTotal += subtotal;
                } else {
                    if (subtotal > ticketTotal) {
                        ticketTotal = subtotal;
                    }
                }
            }
            return map;
        }, res);
        return tabTmpl(tabData);
    });
    var root = '.g-orderOutput_el';
    var btn = root + " .g-total_head [role=\"tab\"]";
    var html = '';
    if (tabs.length > 0) {
        if (window.DISCOUNT_DATA.length > 0) {
            html = tabSetTmpl({ tabs: tabs, discount: window.DISCOUNT_DATA });
        } else {
            html = tabSetTmpl({ tabs: tabs });
        }
    }
    getAll(root).forEach(function (el) { return (el.innerHTML = html); });
    getAll(btn).forEach(function (el) { return el.click(); });
    makeTabsSlidable();
}
function collectDataPack() {
    return getAll('[data-ec-dropdown]').map(function (el) {
        var dataSet = JSON.parse(el.dataset.ecDropdown);
        return {
            el: el,
            dataSet: dataSet,
            code: el.name,
            amount: +el.value,
        };
    });
}
function parseDataPack(kind, dataPacks) {
    var res = [];
    var orderList = dataPacks.filter(function (dp) {
        return (
            dp.dataSet.kind === kind &&
            dp.el.dataset.priority !== undefined &&
            dp.amount > 0
        );
    });

    var liveLimitedList = dataPacks.filter(function (dp) {
        if (kind === "live") {
            return (
                dp.el.dataset.priority !== undefined &&
                dp.dataSet.kind === "l_live"
            );
        }
    });

    var goodsLimitedList = dataPacks.filter(function (dp) {
        if (kind === "goods") {
            return (
                dp.el.dataset.priority !== undefined &&
                dp.dataSet.kind === "l_goods"
            );
        }
    });

    var setLimitedList = dataPacks.filter(function (dp) {
        if (kind === "set") {
            return (
                dp.el.dataset.priority !== undefined &&
                dp.dataSet.kind === "l_set"
            );
        }
    });

    if (orderList.length === 0) {
        return [];
    }

    var orderDataList = orderList.concat(
        liveLimitedList,
        goodsLimitedList,
        setLimitedList
    );


    var collection = new Map();
    orderDataList.forEach(function (item) {
        var priority = +item.el.dataset.priority;
        var array = collection.get(priority) || [];
        array.push(item);
        collection.set(priority, array);
    });
    collection.forEach(function (dataPacks, priority) {
        dataPacks.forEach(function (dp, i) {
            var obj = __assign({}, dp.dataSet);
            delete obj.kind;
            obj.code = dp.code;
            obj.amount = dp.amount;
            obj.priority = dp.el.dataset.priority;
            external_default().set(
                res,
                "[" + priority + "]." + kind + "[" + i + "]",
                obj
            );
        });
    });
    return res;
}
function getCurrentPriority(kind) {
    if (kind === "l_live") kind = "live";
    if (kind === "l_goods") kind = "goods";
    if (kind === "l_set") kind = "set";
    if (!window.ORDER_KIND) {
        if (!window.IS_LOTTERY || (salesMethod === salesMethodLottery && window.IS_MULTIPLE && !window.IS_DIVIDED_PAYMENT)) {
            return window.ORDER_DATA[0] && window.ORDER_DATA[0][kind] ? new Set(window.ORDER_DATA[0][kind].map(m => m.seat_type_id)).size : 0
        }
        return window.ORDER_DATA.length;
    }
    var priority = 0;
    window.ORDER_DATA.forEach(function (data) {
        if (kind in data) {
            priority++;
        }
    });
    return priority;
}
function getContextualSelects(el) {
    var div = el.closest('.g-sellItemSet');
    if (div) {
        return getAll('select', div);
    }
    var dl = el.closest('dl');
    return getAll('select', dl);
}
function getContextualBtnCell(el) {
    var div = el.closest('.g-sellItemSet');
    if (div) {
        return getOne('.g-sellItemSet_btn', div);
    }
    var dl = el.closest('dl');
    return getOne('.g-sellItems_btn', dl);
}
function getContextualDataPacks(el, noPriority) {
    var selects = getContextualSelects(el);
    var dataSet = JSON.parse(selects[0].dataset.ecDropdown);
    var dataPacks = collectDataPack().filter(function (dp) { return dp.dataSet.kind === dataSet.kind && !selects.includes(dp.el); });
    if (noPriority) {
        dataPacks = dataPacks.filter(function (dp) { return dp.el.dataset.priority === undefined; });
    }
    return dataPacks;
}
function getContextualDataPacks2(el, noPriority) {
    var selects = getContextualSelects(el);
    var dataPacks = collectDataPack().filter(function (dp) { return !selects.includes(dp.el); });
    if (noPriority) {
        dataPacks = dataPacks.filter(function (dp) { return dp.el.dataset.priority === undefined; });
    }
    return dataPacks;
}
var registeredTextTmpl = getTmpl('tmplRegisteredText');
/** 座席選択 */
var seatSelectionRegisteredTextTmpl = getTmpl('seatSelectionTmplRegisteredText');
// セットがひとつでも選ばれていたら、もう他のセットは選べないようにする
// 選ばれていなかったら、何もしない
function disableSets() {
    if (window.ORDER_NO_PRIORITY == false) {
        return;
    }
    var dataPacks = collectDataPack();
    var isSetSelected = dataPacks.some(function (dp) { return dp.dataSet.kind === 'set' && dp.el.dataset.priority !== undefined; });
    if (!isSetSelected) {
        return;
    }
    dataPacks.forEach(function (dp) {
        if (dp.dataSet.kind === 'set') {
            dp.el.disabled = true;
        }
    });
}
function updateDropdownStates() {
    var dataPacks = collectDataPack();
    if (!window.ORDER_KIND) {
        var orderDataCount = 0;
        if (window.IS_LOTTERY && salesMethod === salesMethodLottery && window.IS_MULTIPLE && !window.IS_DIVIDED_PAYMENT) {
            orderDataCount = window.ORDER_DATA[0].live.reduce((max, obj) => (parseInt(obj.priority, 10) > max ? parseInt(obj.priority, 10) : max), 0) + 1;
        }
        else orderDataCount = window.ORDER_DATA.length;
        var isFull_1 = window.ORDER_LIMIT === orderDataCount;
        dataPacks.forEach(function (dp) {
            if (dp.el.dataset.priority === undefined) {
                dp.el.disabled = isFull_1;
            }
        });
        disableSets();
        return;
    }
    var currentPriority = { live: -1, goods: -1, set: -1 };
    window.ORDER_DATA.forEach(function (orderData, priority) {
        kinds.forEach(function (kind) {
            if (kind in orderData) {
                currentPriority[kind] = priority;
            }
        });
    });
    kinds.forEach(function (kind) {
        var packs = dataPacks.filter(function (dp) { return dp.dataSet.kind === kind && dp.el.dataset.priority === undefined; });
        var isFull = currentPriority[kind] >= window.ORDER_LIMIT - 1;
        console.log(packs)
        console.log(currentPriority[kind])
        console.log(window.ORDER_LIMIT - 1)
        console.log(isFull)
        packs.forEach(function (dp) { return (dp.el.disabled = isFull); });
    });

}

function combineOrderDataByType(orderData) {
    var data = JSON.parse(JSON.stringify(orderData));
    var arrLive = [];
    var arrGood = [];
    var arrSet = [];
    var dataReturn = {};
    if (data.length === 0) return dataReturn = null;
    else {
        data.forEach((order) => {
            if (order && order['live']) {
                arrLive = [...arrLive, ...order['live']];
            }
            if (order && order['goods']) {
                arrGood = [...arrGood, ...order['goods']];
            }
            if (order && order['set']) {
                arrSet = [...arrSet, ...order['set']];
            }

        })

        if (arrLive.length > 0) {
            dataReturn.live = arrLive;
        }
        if (arrGood.length > 0) {
            dataReturn.goods = arrGood;
        }
        if (arrSet.length > 0) {
            dataReturn.set = arrSet;
        }

        return [dataReturn];
    }
}

var windowBr = window.location.pathname;
var isCheckPathname = windowBr.includes("/purchase/seltickets/");
var isBtnSubmitDefaultDisabled = false;
if (isCheckPathname == true &&  window.IS_LOTTERY ) {
    document.getElementById('btn-submit').disabled = true;
    isBtnSubmitDefaultDisabled = true;
}

function updateOrderData() {
    var dataPacks = collectDataPack();
    var orderData = [];
    external_default().merge(orderData, parseDataPack('live', dataPacks));
    external_default().merge(orderData, parseDataPack('goods', dataPacks));
    external_default().merge(orderData, parseDataPack('set', dataPacks));
    if (!window.IS_LOTTERY || (salesMethod === salesMethodLottery && window.IS_MULTIPLE && !window.IS_DIVIDED_PAYMENT)) {
        window.ORDER_DATA = combineOrderDataByType(orderData) ? combineOrderDataByType(orderData) : [];
    } else {
        window.ORDER_DATA = orderData;
    }
    if (window.IS_DISCOUNT) {
        checkDiscount();
    } else {
        updateTabsByJson();
    }
    if (Array.isArray(window.ORDER_DATA) && window.ORDER_DATA.length) {
        document.getElementById('btn-submit').disabled = false;
    } else if (isBtnSubmitDefaultDisabled) {
        document.getElementById('btn-submit').disabled = true;
    }
}

function handleClick() {
    var selects = window.selects = getContextualSelects(this);
    var dataSet = JSON.parse(selects[0].dataset.ecDropdown);
    var priority = getCurrentPriority(dataSet.kind);
    selects.forEach(function (el) {
        el.dataset.priority = String(priority);
        el.disabled = salesMethod === salesMethodLottery;
    });
    window.ADD_PRODUCT = true;
    updateOrderData();
    var dataPacks = window.ORDER_KIND
        ? getContextualDataPacks(this, true)
        : getContextualDataPacks2(this, true);
    dataPacks.forEach(function (_a) {
        var el = _a.el;
        return (el.disabled = false);
    });
    var dd = getContextualBtnCell(this);
    var html = registeredTextTmpl({ priority: priority });
    dd.innerHTML = html;
    updateDropdownStates();
}
/* 座席選択 */
function seatSelectionHandleClick() {
    var selects = window.selects = getContextualSelects(this);
    var dataSet = JSON.parse(selects[0].dataset.ecDropdown);
    var priority = getCurrentPriority(dataSet.kind);
    selects.forEach(function (el) {
        let method = JSON.parse(atob(document.getElementsByClassName("g-tag")[0].dataset.method));
        salesMethod = method.sales_method;
        salesMethodLottery = method.sales_method_lottery;
        salesMethodFirst = method.sales_method_first;
        el.dataset.priority = String(priority);
        el.disabled = salesMethod === salesMethodLottery;
    });
    window.ADD_PRODUCT = true;
    var dataPacks = window.ORDER_KIND
        ? getContextualDataPacks(this, true)
        : getContextualDataPacks2(this, true);
    dataPacks.forEach(function (_a) {
        var el = _a.el;
        return (el.disabled = false);
    });
    var dd = getContextualBtnCell(this);
    let seatSelectionRegisteredTextTmpl = getTmpl('seatSelectionTmplRegisteredText');
    var html = seatSelectionRegisteredTextTmpl({ priority: priority });
    dd.innerHTML = html;
    updateDropdownStates();

    window.ORDER_DATA.forEach(item => {
        item.live = item.live.filter(liveItem => 
            !(( liveItem.stock_seat_id === "")) 
        );
    });
    updateOrderData();
}
delegate('click', '[data-ec-register]', handleClick);
/* 座席選択 */
delegate('click', '[data-seat-selection-ec-register]', seatSelectionHandleClick);

function handleClear() {
    var myPriority;
    var selects = window.selects = getContextualSelects(this);
    selects.forEach(function (el) {
        if (el.dataset.priority !== undefined) {
            myPriority = +el.dataset.priority;
        }
        delete el.dataset.priority;

        if (salesMethod === salesMethodLottery) {
            el.value = '0';
            el.disabled = false;
        }
    });
    var dataPacks = window.ORDER_KIND
        ? getContextualDataPacks(this, false)
        : getContextualDataPacks2(this, false);
    dataPacks.forEach(function (dp) {
        var priority = dp.el.dataset.priority;
        if (priority !== undefined && +priority > myPriority) {
            var newPriority = +priority - 1;
            dp.el.dataset.priority = String(newPriority);
            var dd_1 = getContextualBtnCell(dp.el);
            var html = registeredTextTmpl({ priority: newPriority });
            dd_1.innerHTML = html;
        }
    });
    var dd = getContextualBtnCell(this);
    dd.innerHTML = '';
    window.ADD_PRODUCT = false;
    updateOrderData();
    updateDropdownStates();
}
/* 座席選択 */
function seatSelectionHandleClear() {
    var myPriority;
    var selects = window.selects = getContextualSelects(this);
    selects.forEach(function (el) {
        if (el.dataset.priority !== undefined) {
            myPriority = +el.dataset.priority;
        }
        delete el.dataset.priority;
        el.value = '0';
        el.disabled = false;
    });
    var dataPacks = window.ORDER_KIND
        ? getContextualDataPacks(this, false)
        : getContextualDataPacks2(this, false);
    dataPacks.forEach(function (dp) {
        var priority = dp.el.dataset.priority;
        if (priority !== undefined && +priority > myPriority) {
            var newPriority = +priority - 1;
            dp.el.dataset.priority = String(newPriority);
            var dd_1 = getContextualBtnCell(dp.el);
            var html = seatSelectionRegisteredTextTmpl({ priority: newPriority });
            dd_1.innerHTML = html;
        }
    });
    var dd = getContextualBtnCell(this);
    dd.innerHTML = '';
    window.ADD_PRODUCT = false;
    updateOrderData();
    updateDropdownStates();
    dd.closest('dl').remove();
}
delegate('click', '[data-ec-clear]', handleClear);
/* 座席選択 */
delegate('click', '[data-seat-selection-ec-clear]', seatSelectionHandleClear);

var registerBtnTmpl = getTmpl('tmplRegisterBtn');
/* #2151 */
var salesMethod;
var salesMethodLottery;
var salesMethodFirst;
document.addEventListener("DOMContentLoaded", () => {
    if(!document.getElementsByClassName("g-tag") || document.getElementsByClassName("g-tag").length == 0 || !document.getElementsByClassName("g-tag")[0].dataset.method){
        return
    }
    let method = JSON.parse(atob(document.getElementsByClassName("g-tag")[0].dataset.method));
    salesMethod = method.sales_method;
    salesMethodLottery = method.sales_method_lottery;
    salesMethodFirst = method.sales_method_first;
});

function handleChange() {
    var dataSet = JSON.parse(this.dataset.ecDropdown);
    var priority = getCurrentPriority(dataSet.kind);
    var dd = getContextualBtnCell(this);

    let isSeatSelection = dd.querySelector("[data-seat-selection-ec-clear]")
        ? true : false;

    let cancel_button;
    if (isSeatSelection) {
        cancel_button = dd.querySelector("[data-seat-selection-ec-clear]");
    } else {
        cancel_button = dd.querySelector("[data-ec-clear]");
    }

    if (cancel_button && salesMethod === salesMethodFirst) {
        cancel_button.click();
    }

    var selects = getContextualSelects(this);
    var dataPacks = window.ORDER_KIND
        ? getContextualDataPacks(this, true)
        : getContextualDataPacks2(this, true);
    var noSelected = dataSet.every
        ? selects.some(function (el) { return el.value === '0'; })
        : selects.every(function (el) { return el.value === '0'; });
    if (noSelected && salesMethod === salesMethodLottery) {
        dd.innerHTML = '';
        dataPacks.forEach(function (_a) {
            var el = _a.el;
            return (el.disabled = false);
        });
        return;
    }

    if (noSelected && isSeatSelection) {
        dd.closest('dl').remove();
        return true;
    }

    var html = registerBtnTmpl({ priority: priority });
    dd.innerHTML = html;

    dataPacks.forEach(function (_a) {
        var el = _a.el;
        return (el.disabled = true);
    });

    if (salesMethod === salesMethodLottery) {
        return true;
    }

    Promise.resolve(dd).then(el => {
        let regist_button = el.querySelector("[data-ec-register]");
        regist_button.click();
    });
}
/* 割引 */
function checkDiscount() {
    var dir = location.pathname.split("/");
    const reception_id = window.RECEPTION_ID ? window.RECEPTION_ID : parseInt(dir[dir.length -1], 10);
    if (window.ADD_PRODUCT) {
        searchDiscount(reception_id);
    } else {
        clearDiscount(reception_id);
    }
    $(document).ajaxComplete(function() {
        updateTabsByJson();
    });
}
function searchDiscount(reception_id) {
    var select_id_list = getSelctIdList(window.selects);
    const url = "/purchase/search_discount";
    const method = "POST";
    const headers = { "X-Requested-With": "XMLHttpRequest", 'X-CSRF-TOKEN': $('input:hidden[name="_token"]').val() };
    const data = {
      reception_id: reception_id,
      order_data: window.ORDER_DATA,
      discount_data: window.DISCOUNT_DATA,
      select_id_list: select_id_list,
    };

    discountCall(url, method, headers, data).done(function(r) {
      if (r.discount_data.length > 0) {
        window.DISCOUNT_DATA = r.discount_data;
      }
    });
};
function clearDiscount(reception_id) {
    var select_id_list = getCancelIdList(window.selects);
    const url = "/purchase/clear_discount";
    const method = "POST";
    const headers = { "X-Requested-With": "XMLHttpRequest", 'X-CSRF-TOKEN': $('input:hidden[name="_token"]').val() }
    const data = {
      reception_id: reception_id,
      order_data: window.ORDER_DATA,
      discount_data: window.DISCOUNT_DATA,
      select_id_list: select_id_list,
    };

    discountCall(url, method, headers, data).done(function(r) {
      window.DISCOUNT_DATA = r.discount_data;
    });
};
function getSelctIdList(selects) {
    var select_id_list = [];
    for(var i = 0; i <selects.length; i++){
        if (selects[i].value > 0) {
            select_id_list.push(selects[i].name);
        }
    }
    return select_id_list;
};
function getCancelIdList(selects) {
    var select_id_list = [];
    for(var i = 0; i <selects.length; i++){
        if (selects[i].value == 0) {
            select_id_list.push(selects[i].name);
        }
    }
    return select_id_list;
};
function discountCall(url, method="GET", headers={}, data=null) {
    return $.ajax({
      "url": url,
      "method": method,
      "timeout": 0,
      "headers": headers,
      "data" : data
    });
}
delegate('change', '[data-ec-dropdown]', handleChange);
  function resetUi() {
    getAll('[data-ec-dropdown]').forEach(function (el) {
      el.disabled = false;
      delete el.dataset.priority;
      el.value = '0';
      var dd = getContextualBtnCell(el);
      dd.innerHTML = '';
    });
  }
  function resetUiType3() {
    getAll('[data-seat-selection-ec-register]').forEach(function (el) {
      el.click();
    });
  }
function resetAll() {
    resetUi();
    window.ORDER_DATA = [];
    updateTabsByJson();
}
delegate('click', '[data-ec-reset]', resetAll);
function handleSubmit() {
    var value = JSON.stringify(window.ORDER_DATA);
    var discount = JSON.stringify(window.DISCOUNT_DATA);
    getOne('input[name="json"]', this).value = value;
    getOne('input[name="discount"]', this).value = discount;
    if (typeof window.SEATSTOCKCONF !== 'undefined' || window.SEATSTOCKCONF) {
        getOne('input[name="is_alert_stock_data"]', this).value = true;
    }
    document.getElementById('btn-submit').disabled = true;
}
delegate('submit', '[data-ec-form]', handleSubmit);
if (window.DISCOUNT_DATA) {
    function selpaySubmit() {
        var discount = JSON.stringify(window.DISCOUNT_DATA);
        getOne('input[name="discount"]', this).value = discount;
        document.getElementById('btn-submit').disabled = true;
    }
    delegate('submit', '[data-selpay-form]', selpaySubmit);
}

function generatePerformanceRequests(performances) {
    if (!performances || (Array.isArray(performances) && performances.length === 0)) {
        return null;
    }
    return createPerformanceRequests(performances).done(function (response) {
        processPerformanceResponse(response);
    }).fail(function () {
        $(".g-sellItems_price").attr("style", "");
    });
}

function generateGoodsRequests(goods) {
    if (!goods || (Array.isArray(goods) && goods.length === 0)) {
        return null;
    }
    return createGoodsRequests(goods).done(function (response) {
        processGoodsResponse(response);
    }).fail(function () {
        $(".g-sellItems_price").attr("style", "");
    });
}

function generateSetTicketRequests(set_tickets) {
    if (!goods || (Array.isArray(set_tickets) && set_tickets.length === 0)) {
        return null;
    }
    return createSetTicketRequests(set_tickets).done(function (response) {
        processSetTicketResponse(response);
    }).fail(function () {
        $(".g-sellItems_price").attr("style", "");
    });
}

function handleAllAjaxRequests(performances, goods, set_tickets) {
    const performanceRequests = generatePerformanceRequests(performances);
    const goodsRequests = generateGoodsRequests(goods);
    const setTicketRequests = generateSetTicketRequests(set_tickets);
    return Promise.all([
        performanceRequests,
        goodsRequests,
        setTicketRequests
    ]);
}

var performances = [];
var goods = [];
var setTickets = [];

function ariaOpenedInit() {
    const trigger_btns = document.querySelectorAll(".g-itemSet_btn_opened");
    for (const trigger_btn of trigger_btns) {
        if (trigger_btn.name === "btn_performance") {
            const performance_id = parseInt(trigger_btn.dataset.performance_id, 10);
            performances.push(performance_id);
        } else if (trigger_btn.name === "btn_good") {
            const good_id = parseInt(trigger_btn.dataset.good_id, 10);
            goods.push(good_id);
        } else if (trigger_btn.name === "btn_set") {
            const set_ticket_id = parseInt(trigger_btn.dataset.set_ticket_id, 10);
            setTickets.push(set_ticket_id);
        } else {
            trigger_btn.click();
            continue;
        }
        const itemWide = trigger_btn.closest('.g-itemSet-list_item-wide')
        const gItemSetRegion = itemWide.querySelector('.g-itemSet_region');
        const gItemSetBtn = itemWide.querySelector('.g-itemSet_btn');
        if (itemWide) {
            gItemSetRegion.setAttribute('aria-hidden', 'false');
            gItemSetBtn.setAttribute('aria-expanded', 'true');
        }
    }
}

function updateUiByJson() {

    if (window.ORDER_READONLY) {
        return;
    }
    ariaOpenedInit();

    const orderData = window.ORDER_DATA
    const serectTickets = window.SERECT_TICKETS


    if (serectTickets.length > 0 && orderData.length == 0) {
        serectTickets.forEach(element => {
            element.items.forEach(e => {
                performances.push(e.performance_id);
            });

        });
    }

    orderData.forEach(element => {
        if (element.live) {
            element.live.forEach(e => {
                performances.push(e.performace_id);
            });
        }
        if (element.goods) {
            element.goods.forEach(e => {
                goods.push(e.good_id);
            });
        }
        if (element.set) {
            element.set.forEach(e => {
                setTickets.push(e.set_ticket_id);
            });
        }
    });

    performances = [...new Set(performances.map(Number))];
    goods = [...new Set(goods.map(Number))];
    setTickets = [...new Set(setTickets.map(Number))];

    handleAllAjaxRequests(performances, goods, setTickets).then(() => {
        orderData.forEach(function (orderData, priority) {
            kinds.forEach(function (kind) {
                var dataSet = orderData[kind];
                if (!dataSet) {
                    return;
                }
                dataSet.forEach(function (data) {
                    var el = getOne(":not(.g-sellItems_amount_limit)>select[name=\"" + data.code + "\"]");
                    const itemWide = el.closest('.g-itemSet-list_item-wide')
                    const gItemSetRegion = itemWide.querySelector('.g-itemSet_region');
                    const gItemSetBtn = itemWide.querySelector('.g-itemSet_btn');
                    if (itemWide) {
                        gItemSetRegion.setAttribute('aria-hidden', 'false');
                        gItemSetBtn.setAttribute('aria-expanded', 'true');
                    }
                    el.value = (el.style.background === "gainsboro") ? 0 : String((parseInt(el.value, 10) || 0) + (parseInt(data.amount, 10) || 0));
                    var selects = getContextualSelects(el);
                    let is_lottery = window.IS_LOTTERY;
                    selects.forEach(function (el) {
                        el.dataset.priority = String(priority);
                        if (is_lottery) {
                            el.disabled = true;
                        }
                    });

                    var dd = getContextualBtnCell(el);
                    const priorityData = window.IS_MULTIPLE ? data.priority : priority;
                    var html = registeredTextTmpl({ priority: priorityData });
                    dd.innerHTML = html;
                    document.getElementById('btn-submit').disabled = false;
                });
            });
        });
    }).catch(error => {
        console.error(error);
    });
}

function createPerformanceRequests(performance_id) {
    return $.ajax({
        url: "/purchase/getPerfomance",
        method: "POST",
        timeout: 0,
        headers: {
            "X-CSRF-TOKEN": $('input[id="csrf-token"]').attr("content"),
        },
        data: {
            performance_id: performance_id,
            reception_id: window.RECEPTION_ID,
        },
        beforeSend: function () {
            $('#loader').removeClass('display-none');
        },
        complete: function () {
            $('#loader').addClass('display-none');
        },
    });
}

    function createGoodsRequests(good_id) {
    return $.ajax({
        url: "/purchase/getPerfomance",
        method: "POST",
        timeout: 0,
        headers: {
            "X-CSRF-TOKEN": $('input[id="csrf-token"]').attr("content"),
        },
        data: {
            good_id: good_id,
            reception_id: window.RECEPTION_ID,
        },
        beforeSend: function () {
            $('#loader_good').removeClass('display-none')
        },
        complete: function () {
            $('#loader_good').addClass('display-none')
        },
    });
}

function createSetTicketRequests(set_ticket_id) {
    return $.ajax({
        url: "/purchase/getPerfomance",
        method: "POST",
        timeout: 0,
        headers: {
            "X-CSRF-TOKEN": $('input[id="csrf-token"]').attr("content"),
        },
        data: {
            set_ticket_id: set_ticket_id,
            reception_id: window.RECEPTION_ID,
        },
        beforeSend: function () {
            $('#loader_set').removeClass('display-none')
        },
        complete: function () {
            $('#loader_set').addClass('display-none')
        },
    });
}

function processPerformanceResponse(response) {
    const option_performanes = [];
    for (let i = 0; i < response.length; i++) {
        const performance_data = response[i].performance;
        if (performance_data) {
            let option_performane = '<option value="0">- </option>';
            for (let x = performance_data.purchasable_lower_ticket_count; x <= performance_data.purchasable_upper_ticket_count; x = x + performance_data.purchase_unit_ticket_count) {
                if (x != 0) {
                    option_performane += `<option value="${x}">${x}</option>`;
                }
            }
            //$(`select[name='${performance_data.select_id}']`).not('#seat_options_select').html(option_performane);
            option_performanes[performance_data.select_id] = option_performane;
        }
    }
    if (Object.keys(option_performanes).length > 0) {
        const select = document.querySelectorAll("[id^='liveDetail'] select:not(#seat_options_select)");
        select.forEach(function (item) {
            if (item.getAttribute("name") in option_performanes && option_performanes[item.getAttribute("name")]) {
                item.innerHTML = option_performanes[item.getAttribute("name")];
            }
        });
    }
}
function processGoodsResponse(response) {
    const option_goods = [];
    for (let i = 0; i < response.length; i++) {
        const goods_data = response[i].goods;
        if (goods_data) {
            let option_good = '<option value="0">- </option>';
            for (let x = goods_data.purchasable_lower_ticket_count; x <= goods_data.purchasable_upper_ticket_count; x = x + goods_data.purchase_unit_ticket_count) {
                if (x != 0) {
                    option_good += `<option value="${x}">${x}</option>`;
                }
            }
            //$(`select[name='${goods_data.select_id}']`).html(option_good);
            option_goods[goods_data.select_id] = option_good;
        }
    }
    if (Object.keys(option_goods).length > 0) {
        const select = document.querySelectorAll("[id^='goodsDetail'] select:not(#seat_options_select)");
        select.forEach(function (item) {
            if (item.getAttribute("name") in option_goods && option_goods[item.getAttribute("name")]) {
                item.innerHTML = option_goods[item.getAttribute("name")];
            }
        });
    }
}
function processSetTicketResponse(response) {
    const option_sets = [];
    for (let i = 0; i < response.length; i++) {
        const set_ticket_data = response[i].set_ticket;
        if (set_ticket_data) {
            let option_set = '<option value="0">- </option>';
            for (let x = set_ticket_data.purchasable_lower_ticket_count; x <= set_ticket_data.purchasable_upper_ticket_count; x = x + set_ticket_data.purchase_unit_ticket_count) {
                if (x != 0) {
                    option_set += `<option value="${x}">${x}</option>`;
                }
            }
            //$(`select[name='${set_ticket_data.select_id}']`).html(option_set);
            option_sets[set_ticket_data.select_id] = option_set;
        }
    }
    if (Object.keys(option_sets).length > 0) {
        const select = document.querySelectorAll("[id^='setDetail'] select:not(#seat_options_select)");
        select.forEach(function (item) {
            if (item.getAttribute("name") in option_sets && option_sets[item.getAttribute("name")]) {
                item.innerHTML = option_sets[item.getAttribute("name")];
            }
        });
    }
}
function init() {
    const isOrderDataEmpty = !window.ORDER_DATA || window.ORDER_DATA.length === 0;
    const hasSelectedTickets = window.SERECT_TICKETS && window.SERECT_TICKETS.length > 0;
    const isDesignType3 = window.DESIGN_TYPE3;

    if (hasSelectedTickets && isDesignType3) {
        resetUiType3();
    } else {
        resetUi();
    }

    if (!isOrderDataEmpty || hasSelectedTickets) {
        updateUiByJson();
        updateTabsByJson();
        updateDropdownStates();
        if (window.ORDER_NO_PRIORITY) {
            toggleState('no-priority', true);
        }
    } else {
        ariaOpenedInit();
        performances = [...new Set(performances.map(Number))];
        goods = [...new Set(goods.map(Number))];
        setTickets = [...new Set(setTickets.map(Number))];
        handleAllAjaxRequests(performances, goods, setTickets).catch(error => {
            console.error(error);
        });
    }
}

init();

/** 支払・受取選択 */
var payment_radio_elems = document.getElementsByName("payment_code");
var payment_code = (payment_radio_elems) ? selectPaymentCode() : null;
var receipt_radio_elems = document.getElementsByName("receipt_code");
var receipt_code = (receipt_radio_elems) ? selectReceiptCode() : null;
var is_payment_free = false;
if (window.AVAILABILITY_PAYMENT_RECEIPT) {
  var available_payment_receipt = window.AVAILABILITY_PAYMENT_RECEIPT;
  var available_payment_receipt_data = available_payment_receipt['payment_receipt_code'];
  var available_payment_receipt_values = Object.values(available_payment_receipt_data);
  if (available_payment_receipt_values) {
    available_payment_receipt_values.forEach(item => {
      if (item.payment_code === '99') {
        is_payment_free = true;
      }
    });
  }
}

receipt_radio_elems.forEach(element => {
    var receipt_list_elemnt = document.getElementById("receipt_list_" + element.value);
    var receipt_radio_element = document.getElementById("rec_" + element.value);
    receipt_list_elemnt.style.color = "#A9A9A9";
    receipt_radio_element.disabled = true;
});

payment_radio_elems.forEach(element => {
    var payment_list_elemnt = document.getElementById("payment_list_" + element.value);
    if (!window.IS_PAYMENT_PERIOD && element.value === "03"){
        payment_list_elemnt.style.display = "none";
    }
});
if (payment_code) {
    if (window.IS_DISCOUNT) {
        searchDiscountBySelpay();
        $(document).ajaxComplete(function() {
            updateTabsByJson();
            changeCommission();
            setDisablePaymentReceipt()
        });
    } else {
        updateTabsByJson();
        changeCommission();
        setDisablePaymentReceipt()
    }
}
function selectPaymentCode() {
    if (payment_radio_elems) {
        for(var i = 0; i <payment_radio_elems.length; i++){
            if (payment_radio_elems[i].checked) {
                return payment_radio_elems[i].value;
            }
        }
    }
    return null;
}
if (payment_radio_elems) {
    for(var i = 0; i <payment_radio_elems.length; i++){
        payment_radio_elems[i].addEventListener("change", (e) => {
            payment_code = e.target.value;

            receipt_radio_elems.forEach(r => {
                r.checked = false;
            });

            if (window.IS_DISCOUNT) {
                searchDiscountBySelpay();
                $(document).ajaxComplete(function() {
                    updateTabsByJson();
                    changeCommission();
                    setDisablePaymentReceipt()
                });
            } else {
                updateTabsByJson();
                changeCommission();
                setDisablePaymentReceipt()
            }
        });
    }
}
var receipt_radio_elems = document.getElementsByName("receipt_code");
var receipt_code = (receipt_radio_elems) ? selectReceiptCode() : null;
if (receipt_code) {
    if (window.IS_DISCOUNT) {
        searchDiscountBySelpay();
        $(document).ajaxComplete(function() {
            updateTabsByJson();
            changeCommission();
            setDisablePaymentReceipt()
        });
    } else {
        updateTabsByJson();
        changeCommission();
        setDisablePaymentReceipt()
    }
}
var windowBr = window.location.pathname;
    var isCheckPathname = windowBr.includes("/purchase/selpay/");
    if (isCheckPathname == true) {
        const ticket_app_device_id = window.TICKET_APP_DEVICE_ID;
        var receipt_radio_elems = document.getElementsByName("receipt_code");
        var receipt_code = (receipt_radio_elems) ? selectReceiptCode() : null;
        $(function () {
            if (receipt_radio_elems) {
                for(var i = 0; i <receipt_radio_elems.length; i++){
                    receipt_radio_elems[i].addEventListener("change", (e) => {
                        receipt_code =  e.target.value;
                        $('#btn-submit').on('click', function() {
                            if (ticket_app_device_id == 0  && ( receipt_code == 60 || receipt_code == 80)) {
                                $('#ticket_app_modal').modal('show');
                                return false;
                            }
                            return true;
                        });
                        updateTabsByJson();
                        changeCommission();
                        setDisablePaymentReceipt()
                    });
                }
            }
        });
   }
function selectReceiptCode() {
    if (receipt_radio_elems) {
        for(var i = 0; i <receipt_radio_elems.length; i++){
            if (receipt_radio_elems[i].checked) {
                return receipt_radio_elems[i].value;
            }
        }
    }
    return null;
}
if (receipt_radio_elems) {
    for(var i = 0; i <receipt_radio_elems.length; i++){
        receipt_radio_elems[i].addEventListener("change", (e) => {
            receipt_code =  e.target.value;
            if (window.IS_DISCOUNT) {
                searchDiscountBySelpay();
                $(document).ajaxComplete(function() {
                    updateTabsByJson();
                    changeCommission();
                    setDisablePaymentReceipt()
                });
            } else {
                updateTabsByJson();
                changeCommission();
                setDisablePaymentReceipt()
            }
        });
    }
}
function changeCommission() {
    if (receipt_code == '10') {
        $('#fee-contact').css('display','table-row');
        $('#fee-delivery').css('display','none');
        $('#fee-famimaReceipt').css('display','none');
        $('#fee-streaming').css('display','none');
    }
    if (receipt_code == '20') {
        $('#fee-contact').css('display','none');
        $('#fee-delivery').css('display','table-row');
        $('#fee-famimaReceipt').css('display','none');
        $('#fee-streaming').css('display','none');
        $('#fee-qrcode').css('display','none');
        $('#fee-automatic-ticket').css('display','none');
        $('#fee-external').css('display','none');
    }
    if (receipt_code == '30') {
        $('#fee-contact').css('display','none');
        $('#fee-delivery').css('display','none');
        $('#fee-famimaReceipt').css('display','table-row');
        $('#fee-streaming').css('display','none');
        $('#fee-qrcode').css('display','none');
        $('#fee-automatic-ticket').css('display','none');
        $('#fee-external').css('display','none');
    }
    if (receipt_code == '40') {
        $('#fee-contact').css('display','none');
        $('#fee-delivery').css('display','none');
        $('#fee-famimaReceipt').css('display','none');
        $('#fee-streaming').css('display','table-row');
        $('#fee-qrcode').css('display','none');
        $('#fee-automatic-ticket').css('display','none');
        $('#fee-external').css('display','none');
    }
    if (receipt_code == '60') {
        $('#fee-delivery').css('display','none');
        $('#fee-famimaReceipt').css('display','none');
        $('#fee-streaming').css('display','none');
        $('#fee-qrcode').css('display','table-row');
        $('#fee-automatic-ticket').css('display','none');
        $('#fee-external').css('display','none'); 
    }
    if (receipt_code == '70') {
        $('#fee-delivery').css('display','none');
        $('#fee-famimaReceipt').css('display','none');
        $('#fee-streaming').css('display','none');
        $('#fee-qrcode').css('display','none');
        $('#fee-automatic-ticket').css('display','table-row');
        $('#fee-external').css('display','none');
    }
    if (receipt_code == '90') {
        $('#fee-delivery').css('display','none');
        $('#fee-famimaReceipt').css('display','none');
        $('#fee-streaming').css('display','none');
        $('#fee-qrcode').css('display','none');
        $('#fee-automatic-ticket').css('display','none');
        $('#fee-external').css('display','table-row');
    }
    if (receipt_code == '80') {
        $('#fee-delivery').css('display','none');
        $('#fee-famimaReceipt').css('display','none');
        $('#fee-streaming').css('display','none');
        $('#fee-qrcode').css('display','table-row');
    }
    if (payment_code == '02') {
        $('#fee-creca').css('display','table-row');
        $('#fee-famima').css('display','none');
    }
    if (payment_code == '03') {
        $('#fee-creca').css('display','none');
        $('#fee-famima').css('display','table-row');
    }
}
    function setDisablePaymentReceipt() {

    var receipt_list = [];
    var is_payment_free = false;
    var available_payment_receipt = window.AVAILABILITY_PAYMENT_RECEIPT;
    var available_payment_receipt_data = available_payment_receipt['payment_receipt_code'];
    var available_payment_receipt_values = Object.values(available_payment_receipt_data);

    if (available_payment_receipt_values) {
      available_payment_receipt_values.forEach(item => {
        if (item.payment_code === '99') {
          is_payment_free = true;
        }
        if (item.payment_code === payment_code) {
          receipt_list.push(item.receipt_code);
        }
        });

      receipt_radio_elems.forEach(element => {
        var receipt_list_elemnt = document.getElementById("receipt_list_" + element.value);
        var receipt_radio_element = document.getElementById("rec_" + element.value);

        if (is_payment_free == false) {
          receipt_radio_element.disabled = true;
          receipt_list_elemnt.style.color = "#A9A9A9";
        }

        if (receipt_list.includes(element.value)) {
          receipt_radio_element.disabled = false;
          receipt_list_elemnt.style.color = "";
        }
        });
    }

}
function searchDiscountBySelpay() {
    var dir = location.pathname.split("/");
    if (window.RECEPTION_ID) {
        var reception_id = parseInt(window.RECEPTION_ID, 10);
    } else {
        var reception_id = parseInt(dir[dir.length -1], 10);
    }
    const url = "/purchase/search_selpay_discount";
    const method = "POST";
    const headers = { "X-Requested-With": "XMLHttpRequest", 'X-CSRF-TOKEN': $('input:hidden[name="_token"]').val() }
    const data = {
      reception_id: reception_id,
      order_data: window.ORDER_DATA,
      discount_data: window.DISCOUNT_DATA,
      payment_code: payment_code,
      receipt_code: receipt_code,
    };

    discountCall(url, method, headers, data).done(function(r) {
      window.DISCOUNT_DATA = r.discount_data;
    });
};

if (document.getElementById('seat-stock-modal-next-btn') != null) {
    var alert_seat_stock_btn = document.getElementById('seat-stock-modal-next-btn');
    alert_seat_stock_btn.onclick = function() {
        window.SEATSTOCKCONF = true;
        $('#btn-submit').trigger("click");
    }
}
if (document.getElementById('seat-stock-modal-prev-btn')) {
    const alert_seat_stock_close_btn = document.getElementById("seat-stock-modal-prev-btn");
    const csrf_token = document.querySelector("#form_select_ticket input[name='_token']") ? document.querySelector("#form_select_ticket input[name='_token']").value : null;
    if (alert_seat_stock_close_btn && csrf_token) {
        alert_seat_stock_close_btn.addEventListener("click", function() {
            fetch('/release-seat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrf_token
                },
            }).then(response => {
                if (response.ok) {
                    return;
                } else {
                    console.error('Error:');
                    window.location.href = "/release_seat_error";
                }
            }).catch(error => {
                console.error('Error:', error);
            });
        });
    } else {
        console.log("alert_seat_stock_close_btn invalid.");
    }
}

const itemSet_btns_performance = document.getElementsByName("btn_performance");
const itemSet_btns_good = document.getElementsByName("btn_good");
const itemSet_btns_set = document.getElementsByName("btn_set");

for (const trigger_performance of [...itemSet_btns_performance]) {
    trigger_performance.addEventListener("click", seat_selection_click_performance);
}
for (const trigger_good of [...itemSet_btns_good]) {
    trigger_good.addEventListener("click", seat_selection_click_good);
}
for (const trigger_set of [...itemSet_btns_set]) {
    trigger_set.addEventListener("click", seat_selection_click_set);
}

function seat_selection_click_performance() {
    const trigger_performance = this;
    const performance_id = parseInt(trigger_performance.dataset.performance_id, 10);

    const itemWide = trigger_performance.closest('.g-itemSet-list_item-wide');
    if (itemWide) {
        const gSellItems = itemWide.querySelector('.g-sellItems');
        if (gSellItems) {
            const newSellItemsItem = gSellItems.querySelector('#new-g-sellItems_item');
            if (newSellItemsItem) {
                return;
            }
        }
    }

    if (trigger_performance.attributes[3].value == "false") {
    const idx_performance = performances.findIndex((value) => value == performance_id);
        if (idx_performance == -1) {
            performances.push(performance_id);
            handleAllAjaxRequests(performance_id, [], [])
            .catch(error => {
                console.error(error);
            });
        }
    }
}
function seat_selection_click_good() {
    const trigger_good = this;
    const good_id = parseInt(trigger_good.dataset.good_id, 10);

    if (trigger_good.attributes[3].value == "false") {
    const idx_good = goods.findIndex((value) => value == good_id);
        if (idx_good == -1) {
            goods.push(good_id);
            handleAllAjaxRequests([], good_id, [])
            .catch(error => {
                console.error(error);
            });
        }
    }
}
function seat_selection_click_set() {
    const trigger_set = this;
    const set_ticket_id = parseInt(trigger_set.dataset.set_ticket_id, 10);

    if (trigger_set.attributes[3].value == "false") {
    const idx_set_ticket = setTickets.findIndex((value) => value == set_ticket_id);
        if (idx_set_ticket == -1) {
            setTickets.push(set_ticket_id);
            handleAllAjaxRequests([], [], set_ticket_id)
            .catch(error => {
                console.error(error);
            });
        }
    }
}

function summary_selection_click() {
    var screenWidth = window.screen.width;
    const items = document.getElementsByClassName("g-itemSet_summary");
    for (const item of [...items]) {
        const isToggle = item.classList.contains("g-itemSet_summary_toggle");
        if (isToggle || screenWidth <= 1024) {
            item.addEventListener("click", (e) => {
                var button = item.querySelector("button")
                if (
                    button
                    && ["btn-dropdown", "btn_performance", "btn_good", "btn_set"].indexOf(button.getAttribute("name"))  > -1
                    && (isToggle || button.getAttribute("aria-expanded") !== 'true')
                    && e.srcElement.className !== "g-i-text_drop_dow"
                    && e.srcElement.tagName !== "BUTTON"
                ) {
                    button.click()
                }
            });
        }
    }
}
summary_selection_click();
/******/ })()
;
