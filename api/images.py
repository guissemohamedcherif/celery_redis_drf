from api.models import Image
from api.serializers import ImageSerializer
# from icecream import ic
from ast import literal_eval


def get_images(array_images):
    return map(lambda x: serializerImage(x), array_images)


def serializerImage(image):
    imageSerializer = ImageSerializer(data={"picture": image})
    if imageSerializer.is_valid():
        imageSerializer.save()
        return imageSerializer.data["id"]

# def get_tarifs(array_items):
#     tarifs = []
#     for el in array_items:
#         tarifSerializer = TarifSerializer(
#             data={"denomination": el.get('denomination'),
#                   "montant": el.get('montant')
#                 })
#         if tarifSerializer.is_valid():
#             tarifSerializer.save()
#             tarifs.append(tarifSerializer.data['id'])
#     return tarifs

# def modif_tarifs(array_items):
#     tarifs,old_tarifs = [],[]
#     for el in array_items:
#         if "id" in el:
#             tarif = Tarif.objects.get(id=el.get("id"))
#             tarif.denomination = el.get('denomination')
#             tarif.montant = el.get('montant')
#             tarif.save()
#             old_tarifs.append(tarif.id)
#         else:
#             tarifSerializer = TarifSerializer(
#                 data={"denomination": el.get('denomination'),
#                     "montant": el.get('montant')
#                     })
#             if tarifSerializer.is_valid():
#                 tarifSerializer.save()
#                 tarifs.append(tarifSerializer.data['id'])
#     return tarifs,old_tarifs



# def get_details_ordonnance(array_items):
#     details = []
#     for el in array_items:
#         detailOrdonnanceSerializer = DetailOrdonnanceSerializer(
#             data={"prescription": el.get('prescription'),
#                   "posologie": el.get('posologie'),
#                   "commentaire": el.get('commentaire'),
#                 })
#         if detailOrdonnanceSerializer.is_valid():
#             if not Medicament.objects.filter(nom=el.get('prescription').lower()).exists():
#                 Medicament.objects.create(nom=el.get('prescription').lower())
#             detailOrdonnanceSerializer.save()
#             details.append(detailOrdonnanceSerializer.data['id'])
#     return details