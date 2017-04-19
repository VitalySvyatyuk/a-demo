# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logger',
            name='event',
            field=models.CharField(db_index=True, max_length=50, verbose_name='Type of action', choices=[(b'account block', '\u0421\u0447\u0435\u0442 \u0437\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d'), (b'account created', '\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0441\u0447\u0435\u0442\u0430'), (b'account data view exceeded', '\u041f\u0440\u0435\u0432\u044b\u0448\u0435\u043d \u043b\u0438\u043c\u0438\u0442 \u043d\u0430 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440 \u0434\u0430\u043d\u043d\u044b\u0445 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439'), (b'account deleted', '\u0423\u0434\u0430\u043b\u0435\u043d\u0438\u0435 \u0441\u0447\u0435\u0442\u0430'), (b'account password restored', '\u0412\u043e\u0441\u0441\u0442. \u043f\u0430\u0440\u043e\u043b\u044f \u043e\u0442 \u0441\u0447\u0435\u0442\u0430'), (b'account block', '\u0421\u0447\u0435\u0442 \u0440\u0430\u0437\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d'), (b'consultation payment', '\u041e\u043f\u043b\u0430\u0442\u0430 \u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u0446\u0438\u0438'), (b'deposit request created', '\u0421\u043e\u0437\u0434. \u0437\u0430\u044f\u0432\u043a\u0438 \u043d\u0430 \u0432\u0432\u043e\u0434'), (b'document uploaded', '\u0417\u0430\u0433\u0440\u0443\u0436\u0435\u043d \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442'), (b'education payment', '\u041e\u043f\u043b\u0430\u0442\u0430 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u044f'), (b'gcrm contact created', '\u041a\u043e\u043d\u0442\u0430\u043a\u0442 \u0441\u043e\u0437\u0434\u0430\u043d'), (b'gcrm manager changed', '\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0438\u0437\u043c\u0435\u043d\u0451\u043d'), (b'gcrm manager changed by button', '\u041a\u043e\u043d\u0442\u0430\u043a\u0442 \u0432\u0437\u044f\u0442 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u043e\u043c'), (b'gcrm manager changed by request', '\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0438\u0437\u043c\u0435\u043d\u0451\u043d \u043f\u043e \u0437\u0430\u043f\u0440\u043e\u0441\u0443'), (b'gcrm manager rename', '\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0443 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e \u0438\u043c\u044f'), (b'gcrm manager revoke', '\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0443\u0434\u0430\u043b\u0435\u043d'), (b'gcrm manager set new password', '\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0443 \u0438\u0437\u043c\u0435\u043d\u0435\u043d \u043f\u0430\u0440\u043e\u043b\u044c'), (b'gcrm new manager manually', '\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d \u043d\u043e\u0432\u044b\u0439 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0432\u0440\u0443\u0447\u043d\u0443\u044e'), (b'has been taken by manager', '\u0411\u044b\u043b \u0432\u0437\u044f\u0442 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u043e\u043c'), (b'ib manager changed', 'IB-\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0438\u0437\u043c\u0435\u043d\u0451\u043d'), (b'internal transfer', '\u0412\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0439 \u043f\u0435\u0440\u0435\u0432\u043e\u0434'), (b'leverage changed', '\u0421\u043c\u0435\u043d\u0430 \u043f\u043b\u0435\u0447\u0430'), (b'login fail', '\u041d\u0435\u0443\u0434\u0430\u0447\u043d\u044b\u0439 \u043b\u043e\u0433\u0438\u043d'), (b'login ok', '\u0423\u0434\u0430\u0447\u043d\u044b\u0439 \u043b\u043e\u0433\u0438\u043d'), (b'manager changed', '\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0438\u0437\u043c\u0435\u043d\u0451\u043d'), (b'manager reassign request accepted', '\u0417\u0430\u043f\u0440\u043e\u0441 \u043d\u0430 \u0441\u043c\u0435\u043d\u0443 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0430 \u043e\u0434\u043e\u0431\u0440\u0435\u043d'), (b'max loss reached', '\u0421\u0440\u0430\u0431. \u043f\u043e\u0440\u043e\u0433\u0430 \u043e\u0442\u043a\u043b.'), (b'minimal equity changed', '\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u043f\u043e\u0440\u043e\u0433\u0430 \u043e\u0442\u043a\u043b.'), (b'notification ratio changed', '\u0418\u0437\u043c. \u043a\u043e\u044d\u0444\u0444. \u0443\u0432\u0435\u0434\u043e\u043c\u043b.'), (b'options style changed', '\u0421\u043c\u0435\u043d\u044f \u0441\u0442\u0438\u043b\u044f \u043e\u043f\u0446\u0438\u043e\u043d\u043e\u0432'), (b'otp binding created', '\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 OTP'), (b'otp auth fail', '\u041d\u0435\u0443\u0434\u0430\u0447\u043d\u0430\u044f OTP \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u0444.'), (b'otp is lost', 'OTP \u043f\u043e\u0442\u0435\u0440\u044f\u043d'), (b'otp login fail', '\u041d\u0435\u0443\u0434\u0430\u0447\u043d\u044b\u0439 OTP \u043b\u043e\u0433\u0438\u043d'), (b'otp login ok', '\u0423\u0434\u0430\u0447\u043d\u044b\u0439 OTP \u043b\u043e\u0433\u0438\u043d'), (b'otp auth ok', '\u0423\u0434\u0430\u0447\u043d\u0430\u044f OTP \u0430\u0443\u0442\u0435\u043d\u0442\u0438\u0444.'), (b'pamm status update', '\u041e\u0431\u043d. \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u0441\u0447\u0435\u0442\u0430'), (b'password changed fail', '\u041d\u0435\u0443\u0434. \u0441\u043c\u0435\u043d\u0430 \u043f\u0430\u0440\u043e\u043b\u044f'), (b'password changed ok', '\u0423\u0434\u0430\u0447\u043d\u0430\u044f \u0441\u043c\u0435\u043d\u0430 \u043f\u0430\u0440\u043e\u043b\u044f'), (b'password restored', '\u0412\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u0430\u0440\u043e\u043b\u044f'), (b'user validation', '\u0412\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u044f \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430'), (b'profile changed', '\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0444\u0438\u043b\u044f'), (b'profile saved', '\u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0444\u0438\u043b\u044f'), (b'rebate changed', '\u0418\u0437\u043c\u0435\u043d\u0451\u043d \u0432\u043e\u0437\u0432\u0440\u0430\u0442 \u0441\u043f\u0440\u0435\u0434\u0430'), (b'replication ratio changed', '\u0418\u0437\u043c. \u043a\u043e\u044d\u0444\u0444. \u043a\u043e\u043f\u0438\u0440.'), (b'requisit changed', '\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0440\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430'), (b'requisit created', '\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0440\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430'), (b'requisit deleted', '\u0423\u0434\u0430\u043b\u0435\u043d\u0438\u0435 \u0440\u0435\u043a\u0432\u0438\u0437\u0438\u0442\u0430'), (b'requisit validation update', '\u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u0432\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u0438'), (b'user saved', '\u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u0435 \u044e\u0437\u0435\u0440\u0430'), (b'validation ok', '\u0412\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u044f \u043f\u0440\u043e\u0444\u0438\u043b\u044f'), (b'validation revoked', '\u0421\u043d\u044f\u0442\u0438\u0435 \u0432\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u0438'), (b'vps subscription', '\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 GC VPS'), (b'vps subscription extended', '\u041f\u0440\u043e\u0434\u043b\u0435\u043d\u0438\u0435 GC VPS'), (b'webtrader login', '\u041b\u043e\u0433\u0438\u043d \u0432 \u0432\u0435\u0431-\u0442\u0440\u0435\u0439\u0434\u0435\u0440'), (b'withdraw requests group approval reset', '\u0413\u0440\u0443\u043f\u043f\u0430 \u0437\u0430\u044f\u0432\u043e\u043a \u043d\u0430 \u0432\u044b\u0432\u043e\u0434: \u043e\u0434\u043e\u0431\u0440\u0435\u043d\u0438\u0435 \u0441\u043d\u044f\u0442\u043e'), (b'withdraw requests group approval changed', '\u0413\u0440\u0443\u043f\u043f\u0430 \u0437\u0430\u044f\u0432\u043e\u043a \u043d\u0430 \u0432\u044b\u0432\u043e\u0434: \u043e\u0434\u043e\u0431\u0440\u0435\u043d\u0438\u0435 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e'), (b'withdraw requests group closed', '\u0413\u0440\u0443\u043f\u043f\u0430 \u0437\u0430\u044f\u0432\u043e\u043a \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0437\u0430\u043a\u0440\u044b\u0442\u0430'), (b'withdraw requests group created', '\u0413\u0440\u0443\u043f\u043f\u0430 \u0437\u0430\u044f\u0432\u043e\u043a \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0441\u043e\u0437\u0434\u0430\u043d\u0430'), (b'withdraw request committed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434: \u0432\u044b\u043f\u043b\u0430\u0447\u0435\u043d\u043e'), (b'withdraw request created', '\u0421\u043e\u0437\u0434. \u0437\u0430\u044f\u0432\u043a\u0438 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434'), (b'withdraw requests failed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434: \u043d\u0435\u0443\u0434\u0430\u0447\u043d\u043e\u0435 \u0441\u043d\u044f\u0442\u0438\u0435'), (b'withdraw request fast declined', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434: \u0437\u0430\u044f\u0432\u043a\u0430 \u043e\u0442\u043a\u043b\u043e\u043d\u0435\u043d\u0430'), (b'withdraw requests payed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434: \u0443\u0441\u043f\u0435\u0448\u043d\u043e\u0435 \u0441\u043d\u044f\u0442\u0438\u0435 \u0441\u0440\u0435\u0434\u0441\u0442\u0432'), (b'withdraw request ready for payment', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u0433\u043e\u0442\u043e\u0432\u0430 \u043a \u0432\u044b\u043f\u043b\u0430\u0442\u0435'), (b'withdraw request ready for payment reset', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434 \u043d\u0435 \u0433\u043e\u0442\u043e\u0432\u0430 \u043a \u0432\u044b\u043f\u043b\u0430\u0442\u0435'), (b'withdraw requests webmoney plugin payed', '\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0432\u044b\u0432\u043e\u0434: \u0432\u044b\u043f\u043b\u0430\u0442\u0430 \u0447\u0435\u0440\u0435\u0437 \u043f\u043b\u0430\u0433\u0438\u043d')]),
        ),
    ]
