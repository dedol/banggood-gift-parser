class Datatable {
  item = `
    <div class="card table-item m-2" style="width: 18rem;" >
      <a href="" target="_blank" data="item.url">
        <img src="" class="card-img-top" data="item.image">
      </a>
      <div class="card-body">
        <p class="card-text">
          <b>$<span data="item.price"></span></b>
          <span data="item.name"></span>
        </p>
        <p class="mb-0">
        <span class="badge rounded-pill bg-secondary" onclick="" style="cursor: pointer;" data="item.category"></span>
        </p>
      </div>
    </div>
    `;

  data = [];
  show = [];

  pageLimit = 2;

  setData(data) {
    for (let i = 0; i < data.length; i++) {
      data[i]._id = i;
    }

    for (let d of data) {
      let tags = [];
      for (let key of Object.keys(d)) {
        if (!key.startsWith('_'))
          tags.push(`${key}:${d[key]}`);
      }
      d._tags = tags.join(' ');
    }

    this.data = data;
    this.show = data;
  };


  search(query) {
    let qlist = query.toLowerCase().split(' ').filter(q => q.trim() != '');

    let res = this.data;
    for (let q of qlist)
      res = res.filter(item => item._tags.toLowerCase().indexOf(q) > -1)

    this.show = res;
    this.render();
  };


  sort(field, type='string', desc=false) {
    let res = this.show;
    if (type == 'string')
      res.sort((a, b) => a[field].localeCompare(b[field]));

    if (type == 'float')
      res.sort(function(a,b) { return a[field] - b[field];});

    if (desc) res.reverse();
    this.render();
  };

  render(page=1) {
    let start = (page - 1) * this.pageLimit;
    let end = start + this.pageLimit
    let data = this.show.slice(start, end);

    let dataLen = data.length;
    let showedLen = document.querySelectorAll('.table-item').length;

    while (dataLen != showedLen) {
      if (dataLen > showedLen) {
        // create element
        document.querySelector('.table-wrapper').innerHTML += this.item;
      }
      else if (dataLen < showedLen) {
        // remove element
        document.querySelector('.table-item:last-child').remove();
      }
  
      showedLen = document.querySelectorAll('.table-item').length;
    };

    // изменение данных в существующих элементах
    let showedElems = document.querySelectorAll('.table-item');
    for (let i = 0; i < data.length; i++) {
        let item = data[i];
        let elem = showedElems[i];

        elem.querySelector('[data="item.url"]').href = item.url;
        elem.querySelector('[data="item.image"]').src = item.image;
        elem.querySelector('[data="item.name"]').innerHTML = item.name;
        elem.querySelector('[data="item.price"]').innerHTML = item.price;
        elem.querySelector('[data="item.category"]').innerHTML = item.category;
        elem.querySelector('[data="item.category"]').onclick = function() {selectCategory(item.category)};
    }

    this.showPagination(page);
  };

  showPagination(page) {
    let viewRange = 3;
    let pagesCount = Math.ceil(this.show.length / this.pageLimit);

    // Проверка корректности номера страницы
    if (page < 1) page = 1;
    if (page > pagesCount) page = pagesCount;

    // Минимальный номер отображаемой страницы
    let pageMin = page - viewRange;
    if (pageMin < 1) pageMin = 1;
    
    // Максимальный номер отображаемой страницы
    let pageMax = page + viewRange;
    if (pageMax > pagesCount) pageMax = pagesCount;

    let html = '';

    // Если первая страница не видна, то выводим <
    if (pageMin != 1)
      html += `<span class="badge bg-secondary" onclick="table.render(1)" style="cursor: pointer; margin-right: 4px;"><</span>`;

    // Выводим страницы от pageMin до pageMax
    for (let p = pageMin; p <= pageMax; p++) {
      if (p == page)
        html += `<span class="badge bg-primary" onclick="table.render(${p})" style="cursor: pointer; margin-right: 4px;">${p}</span>`;
      else
        html += `<span class="badge bg-secondary" onclick="table.render(${p})" style="cursor: pointer; margin-right: 4px;">${p}</span>`;
    }

    // Если последняя страница не видна, то выводим >
    if (pageMax != pagesCount)
      html += `<span class="badge bg-secondary" onclick="table.render(${pagesCount})" style="cursor: pointer; margin-right: 4px;">></span>`;

    // document.querySelector('.table-pagination').innerHTML = html;

    let paginations = document.querySelectorAll('.table-pagination');
    for (let i = 0; i < paginations.length; i++) {
      paginations[i].innerHTML = html;      
    }

  };
}