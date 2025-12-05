/* eslint-disable */
/* 
    Cron expression validation
    Cron expression fields: second, minute, hour, day, month, week, year
    Returns error message string on error, true on success
*/
export function cronValidate(cronExpression ){
  //返回错误信息用
  var message = '';
  // split cron expression
  var cronParams = cronExpression.split(" ");
  // length must be 6 (without year) or 7 (with year)
  if (cronParams.length < 6 || cronParams.length > 7) {
      return "Cron expression must have 6-7 fields";
  }else{
    // day-of-month and day-of-week: one must be ?, or both *
    if((cronParams[3] == "?" && cronParams[5] != "?") || (cronParams[5] == "?" && cronParams[3] != "?") || (cronParams[3] == "*" && cronParams[5] == "*")){
      // seconds
      message = checkSecondsField(cronParams[0]);
      if (message != true) {
          return message;
      }
 
      // minutes
      message = checkMinutesField(cronParams[1]);
      if (message != true) {
          return message;
      }
 
      // hours
      message = checkHoursField(cronParams[2]);
      if (message != true) {
          return message;
      }
 
      // day-of-month
      message = checkDayOfMonthField(cronParams[3]);
      if (message != true) {
          return message;
      }
 
      // month
      message = checkMonthsField(cronParams[4]);
      if (message != true) {
          return message;
      }
 
      // day-of-week
      message = checkDayOfWeekField(cronParams[5]);
      if (message != true) {
          return message;
      }
 
      // year
      if(cronParams.length>6){
        message = checkYearField(cronParams[6]);
        if (message != true) {
            return message;
        }
      }
 
 
      return true;
    }else{
      return "When day-of-month is specified, day-of-week must be '?', and vice versa"
    }
  }
}
 let message = ''
//检查秒的函数方法
function checkSecondsField(secondsField) {
  return checkField(secondsField, 0, 59, "Second");
}
 
//检查分的函数方法
function checkMinutesField(minutesField) {
  return checkField(minutesField, 0, 59, "Minute");
}
 
//检查小时的函数方法
function checkHoursField(hoursField) {
  return checkField(hoursField, 0, 23, "Hour");
}
 
//检查日期的函数方法
function checkDayOfMonthField(dayOfMonthField) {
  if (dayOfMonthField == "?") {
      return true;
  }
  if (dayOfMonthField.indexOf("L") >= 0) {
      return checkFieldWithLetter(dayOfMonthField, "L", 1, 7, "Day");
  } else if ( dayOfMonthField.indexOf("W") >= 0) {
      return checkFieldWithLetter(dayOfMonthField, "W", 1, 31, "Day");
  } else if (dayOfMonthField.indexOf("C") >= 0) {
      return checkFieldWithLetter(dayOfMonthField, "C", 1, 31, "Day");
  }
  return checkField( dayOfMonthField, 1, 31, "Day");
}
 
//检查月份的函数方法
function checkMonthsField(monthsField) {
  //月份简写处理
  if(monthsField != "*"){
    monthsField=monthsField.replace("JAN", "1");
    monthsField=monthsField.replace("FEB", "2");
    monthsField=monthsField.replace("MAR", "3");
    monthsField=monthsField.replace("APR", "4");
    monthsField=monthsField.replace("MAY", "5");
    monthsField=monthsField.replace("JUN", "6");
    monthsField=monthsField.replace("JUL", "7");
    monthsField=monthsField.replace("AUG", "8");
    monthsField=monthsField.replace("SEP", "9");
    monthsField=monthsField.replace("OCT", "10");
    monthsField=monthsField.replace("NOV", "11");
    monthsField=monthsField.replace("DEC", "12");
    return checkField(monthsField, 1, 12, "Month");
  }else{
    return true;
  }
 
}
 
//星期验证
function checkDayOfWeekField(dayOfWeekField) {
  dayOfWeekField=dayOfWeekField.replace("SUN", "1" );
  dayOfWeekField=dayOfWeekField.replace("MON", "2" );
  dayOfWeekField=dayOfWeekField.replace("TUE", "3" );
  dayOfWeekField=dayOfWeekField.replace("WED", "4" );
  dayOfWeekField=dayOfWeekField.replace("THU", "5" );
  dayOfWeekField=dayOfWeekField.replace("FRI", "6" );
  dayOfWeekField=dayOfWeekField.replace("SAT", "7" );
  if (dayOfWeekField == "?") {
    return true;
  }
  if (dayOfWeekField.indexOf("L") >= 0) {
      return checkFieldWithLetterWeek(dayOfWeekField, "L", 1, 7, "Week");
  } else if (dayOfWeekField.indexOf("C") >= 0) {
      return checkFieldWithLetterWeek(dayOfWeekField, "C", 1, 7, "Week");
  } else if (dayOfWeekField.indexOf("#") >= 0) {
      return checkFieldWithLetterWeek(dayOfWeekField, "#", 1, 7, "Week");
  } else {
      return checkField(dayOfWeekField, 1, 7, "Week");
  }
}
 
//检查年份的函数方法
function checkYearField(yearField) {
  return checkField(yearField, 1970, 2099, "Year");
}
 
//通用的检查值的大小范围的方法( - , / *)
function checkField(value, minimal, maximal, attribute) {
  // has '-'
  if (value.indexOf("-") > -1 ) {
    return checkRangeAndCycle(value, minimal, maximal,attribute);
  }
  // has ','
  else if (value.indexOf(",") > -1) {
    return checkListField(value, minimal, maximal,attribute);
  }
  // has '/'
  else if (value.indexOf( "/" ) > -1) {
    return checkIncrementField( value, minimal, maximal ,attribute);
  }
  // is '*'
  else if (value=="*") {
    return true;
  }
  // single number or alpha
  else {
    return checkIntValue(value, minimal, maximal,true, attribute);
  }
}
 
 
//检测是否是整数以及是否在范围内,参数：检测的值，下限，上限，是否检查端点，检查的属性
function checkIntValue(value, minimal, maximal, checkExtremity,attribute) {
  try {
      // parse as base-10 integer
      var val = parseInt(value, 10);
      if (value == val) {
          if (checkExtremity) {
              if (val < minimal || val > maximal) {
                  return (attribute+" must be between "+ minimal + "-" + maximal);
              }
              return true;
          }
          return true;
      }
      return (attribute+" contains invalid characters; must be an integer or allowed uppercase letter");
  } catch (e) {
      return (attribute+" contains invalid characters; must be an integer")
  }
}
//检验枚举类型的参数是否正确
function checkListField(value, minimal, maximal,attribute) {
  var st = value.split(",");
  var values = new Array(st.length);
  //计算枚举的数字在数组中中出现的次数，出现一次为没有重复的。
  var count=0;
  for(var j = 0; j < st.length; j++) {
      values[j] = st[j];
  }
  //判断枚举类型的值是否重复
  for(var i=0;i<values.length;i++){
    //判断枚举的值是否在范围内
    message = checkIntValue(values[i], minimal, maximal, true, attribute);
    if (message!=true) {
      return message;
    }
    count=0;
    for(var j=0;j<values.length;j++){
      if(values[i]==values[j])
      {
        count++;
      }
      if(count>1){
        return (attribute+" values contain duplicates");
      }
    }
  }
  var previousValue = -1;
  //判断枚举的值是否排序正确
  for (var i= 0; i < values.length; i++) {
      var currentValue = values[i];
      try {
          var val = parseInt(currentValue, 10);
          if (val < previousValue) {
              return (attribute+" values must be sorted ascending");
          } else {
              previousValue = val;
          }
      } catch (e) {
        // not reachable
        return ("not used")
      }
  }
  return true;
}
 
//检验循环
function checkIncrementField(value, minimal, maximal, attribute) {
  if(value.split("/").length>2){
    return (attribute + " can contain only one '/'");
  }
  var start = value.substring(0, value.indexOf("/"));
  var increment = value.substring(value.indexOf("/") + 1);
  if (start != "*") {
    //检验前值是否正确
    message = checkIntValue(start, minimal, maximal, true, attribute);
    if(message != true){
      return message;
    }
    //检验后值是否正确
    message = checkIntValue(increment, minimal, maximal, true, attribute);
    if(message != true){
      return message;
    }
    return true;
  } else {
    //检验后值是否正确
    return checkIntValue(increment, minimal, maximal, false, attribute);
  }
}
 
//检验范围
function checkRangeAndCycle(params, minimal, maximal, attribute){
  // only one '-'
  if(params.split("-").length>2){
    return (attribute + " can only have one '-'");
  }
  var value = null;
  var cycle = null;
  //检验范围内是否有嵌套周期
  if(params.indexOf("/") > -1){
    // only one '/'
    if(params.split("/").length>2){
      return (attribute + " can only have one '/'");
    }
    value = params.split("/")[0];
    cycle = params.split("/")[1];
    // validate cycle
    message =checkIntValue(cycle, minimal, maximal, true, attribute);
    if (message!=true) {
      return message;
    }
  }else{
    value = params;
  }
  var startValue = value.substring(0, value.indexOf( "-" ));
  var endValue = value.substring(value.indexOf( "-" ) + 1);
  // validate start value
  message =checkIntValue(startValue, minimal, maximal, true, attribute);
  if (message!=true) {
    return message;
  }
  // validate end value
  message =checkIntValue(endValue, minimal, maximal, true, attribute);
  if(message!=true){
    return message;
  }
  // end must be >= start
  try {
    var startVal = parseInt(startValue, 10);
    var endVal = parseInt(endValue, 10);
    if(endVal < startVal){
      return (attribute+" range invalid: start must be <= end");
    }
    if((endVal-startVal)<parseInt(cycle,10)){
      return (attribute+" cycle range invalid");
    }
    return true;
  } catch (e) {
    // not used
    return (attribute+" contains invalid characters; must be an integer");
  }
}
 
//检查日中的特殊字符
function checkFieldWithLetter(value, letter, minimalBefore, maximalBefore,attribute) {
  // only one letter
  for(var i=0;i<value.length;i++){
    var count = 0;
    if(value.charAt(i)==letter){
      count++;
    }
    if(count>1){
      return (attribute+" letter '"+letter+"' can appear only once")
    }
  }
  // L
  if(letter == "L"){
    if(value == "LW"){
      return true;
    }
    if(value=="L"){
      return true;
    }
    if(value.endsWith("LW")&&value.length>2)
    {
      return ("For 'LW', no letter allowed before 'LW'")
    }
    if(!value.endsWith("L"))
    {
      return ("For 'L', only 'LW' allowed; no other chars after 'L'")
    }else{
      var num = value.substring(0,value.indexOf(letter));
      return checkIntValue(num, minimalBefore, maximalBefore, true, attribute);
    }
  }
 
  // W
  if(letter == "W"){
    if(!value.endsWith("W")){
      return ("'W' must be at the end")
    }else{
      if(value=="W"){
        return ("'W' must be preceded by a number")
      }
      var num = value.substring(0,value.indexOf(letter));
      return checkIntValue(num, minimalBefore, maximalBefore, true, attribute);
    }
  }
 
  if(letter == "C"){
    if(!value.endsWith("C")){
      return ("'C' must be at the end")
    }else{
      if(value=="C"){
        return ("'C' must be preceded by a number")
      }
      var num = value.substring(0,value.indexOf(letter));
      return checkIntValue(num, minimalBefore, maximalBefore, true, attribute);
    }
  }
}
 
//检查星期中的特殊字符
function checkFieldWithLetterWeek(value, letter, minimalBefore, maximalBefore,attribute) {
  // only one letter
  for(var i=0;i<value.length;i++){
    var count = 0;
    if(value.charAt(i)==letter){
      count++;
    }
    if(count>1){
      return (attribute+" letter '"+letter+"' can appear only once")
    }
  }
  // L
  if(letter == "L"){
    if(value=="L"){
      return true;
    }
    if(!value.endsWith("L"))
    {
      return ("'L' must be at the end")
    }else{
      var num = value.substring(0,value.indexOf(letter));
      return checkIntValue(num, minimalBefore, maximalBefore, true, attribute);
    }
  }
 
  if(letter == "C"){
    if(!value.endsWith("C")){
      return ("'C' must be at the end")
    }else{
      if(value=="C"){
        return ("'C' must be preceded by a number")
      }
      var num = value.substring(0,value.indexOf(letter));
      return checkIntValue(num, minimalBefore, maximalBefore, true, attribute);
    }
  }
 
  if(letter == "#"){
    if(value=="#"){
      return ("There must be integers on both sides of '#'");
    }
    if(value.charAt(0)==letter){
      return ("There must be an integer before '#'");
    }
    if(value.endsWith("#")){
      return ("There must be an integer after '#'");
    }
    var num1 = value.substring(0,value.indexOf(letter));
    var num2 = value.substring(value.indexOf(letter)+1,value.length);
    message = checkIntValue(num1, 1, 4, true, (attribute+" before '#'"));
    if(message!=true){
      return message;
    }
    message = checkIntValue(num2, minimalBefore, maximalBefore, true, (attribute+" after '#'"));
    if(message!=true){
      return message;
    }
    return true;
  }
}