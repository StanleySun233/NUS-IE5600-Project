import folium
from folium.plugins import TimestampedGeoJson

# 初始化地图
m = folium.Map(location=[30, 120], zoom_start=10)

# 使用JavaScript滑动条和悬浮窗
slider_html = '''
<script>
  var slider = document.createElement("input");
  slider.type = "range";
  slider.min = "0";
  slider.max = "1440";  // 24小时，每分钟为一个步长
  slider.value = "0";
  slider.step = "1";
  document.body.appendChild(slider);

  var dateInput = document.createElement("input");
  dateInput.type = "date";
  document.body.appendChild(dateInput);

  // 监听滑动条和日期选择事件
  slider.oninput = function() {
    updateMap(this.value);  // 更新地图，根据时间步长
  }

  dateInput.oninput = function() {
    updateDate(this.value);  // 更新日期，获取新数据
  }

  function updateMap(timeStep) {
    // 这里与后端交互获取当前时间步长对应的船舶位置
    fetch(`/update_map?time_step=${timeStep}&date=${dateInput.value}`)
      .then(response => response.json())
      .then(data => {
        // 更新船舶位置与轨迹
      });
  }

  function updateDate(date) {
    // 选择日期，向后端请求船舶数据
    fetch(`/fetch_data?date=${date}`)
      .then(response => response.json())
      .then(data => {
        // 渲染船舶数据
      });
  }
</script>
'''

# 将HTML嵌入地图
m.get_root().html.add_child(folium.Element(slider_html))

# 保存并显示地图
m.save('index.html')
