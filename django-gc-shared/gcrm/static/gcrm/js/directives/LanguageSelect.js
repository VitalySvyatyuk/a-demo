angular.module('GCRM').component('languageSelect', {
  bindings: {
    model: '=',
    onChange: '&',
    languages: '='
  },
  templateUrl: '/gcrm/templates/component.languageSelect.html',
  controllerAs: 'languageSelect',
  controller: function ($timeout) {
    this.model = this.model || []
    this.selectedLanguage = []
    if (this.model.length && !this.selectedLanguage.length) {
      for (let lang of this.languages) {
        if (this.model.indexOf(lang[0]) + 1) {
          this.selectedLanguage.push(lang)
        }
      }
    }

    this.isSelectedLang = (item) => {
      return (this.selectedLanguage.indexOf(item) + 1); 
    }
    
    this.addLanguage = (item) => {
      this.model.push(item[0])
      this.languageName = undefined
      $timeout(this.onChange.bind(this), 1);
    }

    this.removeLanguage = (item) => {
      this.model.splice(this.model.indexOf(item[0]), 1)
      $timeout(this.onChange.bind(this), 1);
    }
  }
})
