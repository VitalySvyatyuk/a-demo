$(function () {

	var doc = $('#id_no_documents').parent();
	var no_doc = $('#id_documents').parent();
	var oferta = $('#id_oferta_agreement').parent();


	$("#id_type_of_agreement_0").change(function(){oferta.show();doc.hide();no_doc.hide();});
	$("#id_type_of_agreement_1").change(function(){doc.show();no_doc.show();oferta.hide();});
	doc.hide();
	no_doc.hide();
	oferta.hide();
});

