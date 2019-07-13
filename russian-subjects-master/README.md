# Российские Округа, Регионы, Города. JSON #

В репозитории есть два варианта: native и alternative.
Альтернативная версия JSON, отличается меньшим количеством городов, так же было замечено, что отсутствуют некоторые города. Например, не был обнаружен Калининград.<br>
В списках нет Крымской АР / Республики Крым

У каждого города в списках есть собственная геометка.

Переменные в массиве позволяют быстро выстроить relation-связи в таблице БД:
* внутри **cities.json** у каждого элемента есть *region_id*, *district_id*
* внутри **regions.json** у каждого элемента есть *district_id*

<br>

<table>
  <thead>
    <tr>
    <th>Список</th><th>Округов</th><th>Регионов</th><th>Городов</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>native</th>
      <td>8</td>
      <td>78</td>
      <td>2513</td>
    </tr>
    <tr>
      <th>alternative</th>
      <td>8</td>
      <td>83</td>
      <td>447</td>
    </tr>
    <tr>
      <th>Примеры</th>
      <td>Центральный округ</td>
      <td>Москва и Московская область</td>
      <td>Москва</td>
    </tr>
  </tbody>  
</table>

## Credits ##
* <a href="https://github.com/kvrvch">kvrvch</a>

## License MIT ##

## Tags ##
*Russian Cities, Regions, Districts JSON. Российские города, области, края, ао, республики, регионы, округи JSON. API. 
with geodata geocodes, с геометками. Без Крыма (Крымской АР / Республики Крым)*