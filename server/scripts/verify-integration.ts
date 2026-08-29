import { PrismaClient } from "@prisma/client";
const db=new PrismaClient();
async function main(){
  await db.$queryRaw`SELECT 1`;
  const [roles,clearances,permissions,subjects,graphNodes,graphEdges,snapshots,gnnNodes,gnnEdges,embeddings,transactions,investigations,runs,findings,evidence,audits]=await Promise.all([db.role.count(),db.clearanceLevel.count(),db.permission.count(),db.subject.count(),db.graphNode.count(),db.graphEdge.count(),db.gnnGraphSnapshot.count(),db.gnnNode.count(),db.gnnEdge.count(),db.gnnEmbedding.count(),db.transaction.count(),db.investigation.count(),db.analysisRun.count(),db.investigationFinding.count(),db.evidenceReference.count(),db.auditEvent.count()]);
  const latest=await db.analysisRun.findFirst({orderBy:{createdAt:"desc"},select:{id:true,status:true,aiEngineVersion:true,requestedBy:true,modelVersions:true,completedAt:true}});
  console.log(JSON.stringify({status:"ok",access:{roles,clearances,permissions},canonical:{subjects,transactions},graph:{graphNodes,graphEdges,snapshots,gnnNodes,gnnEdges,embeddings},workflow:{investigations,runs,findings,evidence,audits,latest}},null,2));
}
main().finally(()=>db.$disconnect());
