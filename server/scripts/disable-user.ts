import { PrismaClient } from "@prisma/client";
const email=process.argv[2]; if(!email) throw new Error("Usage: node --experimental-strip-types scripts/disable-user.ts <email>");
const db=new PrismaClient();
async function main(){const user=await db.user.findUnique({where:{email}}); if(!user)return console.log(JSON.stringify({status:"not_found"})); await db.$transaction([db.authSession.updateMany({where:{userId:user.id,revokedAt:null},data:{revokedAt:new Date()}}),db.user.update({where:{id:user.id},data:{status:"DISABLED"}})]); console.log(JSON.stringify({status:"disabled",userId:user.id}));}
main().finally(()=>db.$disconnect());
