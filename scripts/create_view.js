// Запуск: mongosh mongodb://localhost:27017/EdTechDB create_view.js
db.createView("bd_online_aggregated", "lessons", [
  { $lookup: { from: "attendances", localField: "_id", foreignField: "lessonId", as: "attendance_docs" } },
  { $unwind: "$attendance_docs" },
  { $lookup: { from: "groups", localField: "groupId", foreignField: "_id", as: "group_docs" } },
  { $unwind: "$group_docs" },
  { $match: { "group_docs.filial": "63c63702397ca6783eb57fa2" } },
  { $project: { _id: 0, date: "$date", lessonId: "$_id" } }
]);
