#coding=utf-8

from django.db import models

class TypicalCommentsCategory(models.Model):
    name = models.CharField(u"Название категории", max_length=250)

    class Meta:
        verbose_name = u'Категория типовых комментариев'
        verbose_name_plural = u'Категории типовых комментариев'

    def __unicode__(self):
        return self.name
        

class TypicalComment(models.Model):
    text = models.TextField(u"Текст типового комментария")
    creation_ts = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey("TypicalCommentsCategory", verbose_name=u"Категория типового комментария")

    class Meta:
        verbose_name = u'Типовой комментарий'
        verbose_name_plural = u'Типовые комментарии'
        ordering = ('-creation_ts', )

    def __unicode__(self):
        return self.text